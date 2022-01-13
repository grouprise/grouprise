import copy
import functools
import logging
import random
import string
import sys
import time

import markdown
import nio
from django.core.exceptions import ObjectDoesNotExist

from grouprise.core.templatetags.defaultfilters import full_url

from . import MatrixBackend
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)
from .settings import MATRIX_SETTINGS
from .utils import get_matrix_notification_room_queryset

logger = logging.getLogger(__name__)


# this variable serves as a trivial per-process cache for the latest sync timestamp
# see https://git.hack-hro.de/grouprise/grouprise/-/issues/755
_latest_sync_token = None


class MatrixError(Exception):
    """an error occurred while communicating with the matrix server"""


class MatrixClient(nio.AsyncClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_event_callback(self.cb_autojoin_room, nio.InviteEvent)
        self.matrix_bot = None

    async def cb_autojoin_room(self, room: nio.MatrixRoom, event: nio.InviteEvent):
        await self.join(room.room_id)
        if self.matrix_bot:
            try:
                room_object = MatrixChatGroupRoom.objects.get(room_id=room.room_id)
            except MatrixChatGroupRoom.DoesNotExist:
                pass
            else:
                await self.matrix_bot.configure_group_room(room_object)


class MatrixBot:
    def __init__(self):
        matrix_url = f"https://{MATRIX_SETTINGS.DOMAIN}"
        self.bot_matrix_id = f"@{MATRIX_SETTINGS.BOT_USERNAME}:{MATRIX_SETTINGS.DOMAIN}"
        logger.info(f"Connecting to {matrix_url} as '{MATRIX_SETTINGS.BOT_USERNAME}'")
        if MATRIX_SETTINGS.BACKEND == MatrixBackend.NIO:
            self.client = MatrixClient(matrix_url, self.bot_matrix_id)
            # maybe we should use "self.client.login()" instead?
        elif MATRIX_SETTINGS.BACKEND == MatrixBackend.CONSOLE:
            self.client = MatrixConsoleClient()
        else:
            raise NotImplementedError(
                f"The selected Matrix Chat backend is not supported: {MATRIX_SETTINGS.BACKEND}"
            )
        self.client.matrix_bot = self
        self.client.access_token = MATRIX_SETTINGS.BOT_ACCESS_TOKEN

    async def sync(self, set_presence="online", since=None, update_period=None):
        """synchronize the bot state with the server state

        If "update_period" is specified, then the function is running forever and
        polls for new events.  The period defines the maximum duration of a request,
        even if no events are received.  Callbacks are executed immediately anyway.
        """
        global _latest_sync_token
        if since is None:
            since = _latest_sync_token
        if update_period is None:
            sync_function = self.client.sync
        else:
            period_sec = 1000 * update_period
            sync_function = functools.partial(self.client.sync_forever, period_sec)
        sync_result = await sync_function(set_presence=set_presence, since=since)
        if isinstance(sync_result, nio.responses.SyncError):
            raise MatrixError(
                f"Failed to synchronize state with homeserver: {sync_result}"
            )
        if not self.client.logged_in:
            raise MatrixError(
                "Failed to login. There is a problem with the matrix server or the configured "
                "account settings are invalid."
            )
        _latest_sync_token = sync_result.next_batch

    async def __aenter__(self):
        try:
            await self.sync()
        except MatrixError:
            try:
                await self.close()
            except Exception:
                pass
            raise
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
        return False

    async def close(self):
        await self.client.close()

    async def send_text(
        self, room_id: str, body: str, msgtype="m.notice", parser="markdown"
    ):
        msg = {"body": body, "msgtype": msgtype}
        if parser == "markdown":
            msg["format"] = "org.matrix.custom.html"
            msg["formatted_body"] = markdown.markdown(body)
        try:
            response = await self.client.room_send(room_id, "m.room.message", msg)
        except nio.exceptions.ProtocolError as exc:
            raise MatrixError(f"Failed to send message: {exc}")
        else:
            if not isinstance(response, nio.responses.RoomSendResponse):
                raise MatrixError(f"Failed to send message: {response}")

    async def synchronize_rooms_of_group(self, group):
        """create rooms for the group and synchronize their avatar with the grouprise avatar"""
        for is_private in (False, True):
            try:
                room, created = await self._get_or_create_group_room(group, is_private)
            except MatrixError as exc:
                logger.error(f"Failed to create room: {exc}")
            else:
                if created:
                    yield room
                await self.configure_group_room(room)

    async def _get_or_create_group_room(self, group, is_private):
        try:
            room = MatrixChatGroupRoom.objects.get(group=group, is_private=is_private)
            return room, False
        except MatrixChatGroupRoom.DoesNotExist:
            pass
        # the room does not exist: we need to create it
        group_url = full_url(group.get_absolute_url())
        if is_private:
            room_title = "{} (private)".format(group.name)
            room_description = "{} - members only".format(group_url)
        else:
            room_title = group.name
            room_description = group_url
        preset = (
            nio.api.RoomPreset.private_chat
            if is_private
            else nio.api.RoomPreset.public_chat
        )
        visibility = (
            nio.api.RoomVisibility.private
            if is_private
            else nio.api.RoomVisibility.public
        )
        try:
            response = await self.client.room_create(
                name=room_title,
                topic=room_description,
                preset=preset,
                visibility=visibility,
            )
        except nio.exceptions.ProtocolError as exc:
            raise MatrixError(f"Failed to create room '{room_title}': {exc}")
        if not isinstance(response, nio.responses.RoomCreateResponse):
            raise MatrixError(
                f"Create room requested for '{room_title}' was rejected: {response}"
            )
        # store the room
        room = MatrixChatGroupRoom.objects.create(
            group=group, is_private=is_private, room_id=response.room_id
        )
        # respond with success, even though the alias assignment may have failed
        return room, True

    async def configure_group_room(self, room):
        room_alias = room.get_default_room_alias()
        # try to set the visibility of the room in the public room directory
        try:
            response = await self.client._send(
                nio.responses.EmptyResponse,
                "PUT",
                nio.api.Api._build_path(
                    ["directory", "list", "room", room.room_id],
                    {"access_token": self.client.access_token},
                ),
                data=nio.api.Api.to_json(
                    {
                        "visibility": (
                            nio.api.RoomVisibility.private
                            if room.is_private
                            else nio.api.RoomVisibility.public
                        ).value
                    }
                ),
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to set visibility of room ({room_alias}): {exc}")
        else:
            if not isinstance(response, nio.responses.EmptyResponse):
                logger.warning(
                    f"Refused to set visibility of room ({room_alias}): {response}"
                )
        # try to assign a local alias to the room
        try:
            response = await self.client._send(
                nio.responses.EmptyResponse,
                "PUT",
                nio.api.Api._build_path(
                    ["directory", "room", room_alias],
                    {"access_token": self.client.access_token},
                ),
                data=nio.api.Api.to_json({"room_id": room.room_id}),
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to assign alias ({room_alias}) to room: {exc}")
        else:
            # we cannot detect the state of an alias already existing, thus we parse the message
            if not isinstance(
                response, nio.responses.EmptyResponse
            ) and not response.message.endswith(" already exists"):
                logger.warning(
                    f"Refused to assign alias ({room_alias}) to room: {response}"
                )
        # try to tell the room about its alias
        try:
            response = await self.client.room_put_state(
                room.room_id,
                "m.room.aliases",
                {"alias": [room_alias]},
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to tell room its alias ({room_alias}): {exc}")
        else:
            if not isinstance(response, nio.responses.RoomPutStateResponse):
                logger.warning(
                    f"Refused to memorize alias for room ({room_alias}): {response}"
                )
        # try to set the alias as canonical
        try:
            response = await self.client.room_put_state(
                room.room_id,
                "m.room.canonical_alias",
                {"alias": room_alias},
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(
                f"Failed to set canonical alias ({room_alias}) of room: {exc}"
            )
        else:
            if not isinstance(response, nio.responses.RoomPutStateResponse):
                logger.warning(
                    f"Refused to set canonical alias ({room_alias}) of room: {response}"
                )
        # try to raise default role of new members
        if not await self._change_room_state(
            room.room_id,
            {"users_default": 50},
            "m.room.power_levels",
            room_label=str(room),
        ):
            logger.warning(
                f"Failed to raise default role for new members ({room_alias})"
            )

    async def create_private_room(self, room_title, room_description):
        try:
            response = await self.client.room_create(
                name=room_title,
                topic=room_description,
                preset=nio.api.RoomPreset.private_chat,
                visibility=nio.api.RoomVisibility.private,
            )
        except nio.exceptions.ProtocolError as exc:
            raise MatrixError(f"Failed to create room '{room_title}': {exc}")
        if not isinstance(response, nio.responses.RoomCreateResponse):
            raise MatrixError(
                f"Create room requested for '{room_title}' was rejected: {response}"
            )
        return response.room_id

    async def get_public_room_name(self, room_id: str):
        """try to determine a "routable" room name

        Room IDs should be treated as internal implementation details and should not be used in
        URLs, if possible (see https://github.com/vector-im/element-web/issues/2925).
        Instead one of the room's aliases should be used.
        This function returns the canonical alias (if it exists) or the first (alphabetically) of
        the other aliases.
        Returns 'None' if no alias is found.
        """
        canonical_state = await self._get_room_state(room_id, "m.room.canonical_alias")
        if canonical_state:
            return canonical_state["alias"]
        else:
            aliases_state = await self._get_room_state(room_id, "m.room.aliases")
            if aliases_state and aliases_state["alias"]:
                return sorted(aliases_state["alias"])[0]
            else:
                return None

    async def remove_room_alias(self, room_id: str, room_alias: str):
        canonical_state = await self._get_room_state(room_id, "m.room.canonical_alias")
        if canonical_state and (canonical_state["alias"] == room_alias):
            await self._change_room_state(
                room_id, {"alias": None}, "m.room.canonical_alias"
            )
        aliases_state = await self._get_room_state(room_id, "m.room.aliases")
        if aliases_state:
            aliases = aliases_state["alias"]
            if room_alias in aliases:
                aliases.remove(room_alias)
                await self._change_room_state(
                    room_id, {"alias": aliases}, "m.room.aliases"
                )

    async def _get_room_state(self, room_id, state_key):
        try:
            response = await self.client.room_get_state(room_id)
            failure_reason = None
        except nio.exceptions.ProtocolError as exc:
            response = None
            failure_reason = exc
        if not isinstance(response, nio.responses.RoomGetStateResponse):
            error_message = failure_reason or response
            logger.warning(f"Failed to get room state ({room_id}): {error_message}")
            return None
        matching_events = [
            event for event in response.events if event["type"] == state_key
        ]
        if matching_events:
            return matching_events[0]["content"]
        else:
            return {}

    async def _change_room_state(
        self, room_id: str, changes: dict, state_key: str, room_label=None
    ):
        """configure the power levels, aliases and other attributes of a room

        The procedure is a bit complicated, since we need to send a full state dictionary.
        Thus we retrieve the current state first and merge it with the wanted changes.
        The result is sent to the server (if it differs from the current state).

        Specification: https://matrix.org/docs/spec/client_server/latest#id253
        """
        state_label = state_key.split(".")[-1].replace("_", " ")
        if room_label is None:
            room_label = room_id
        # retrieve the current state
        original_state = await self._get_room_state(room_id, state_key)
        if original_state is None:
            logger.warning(
                f"Failed to retrieve current state before changing '{state_key}' in room"
                f" '{room_label}'"
            )
            return False
        wanted_state = copy.deepcopy(original_state)
        # merge the current state with the wanted changes
        for key, value in changes.items():
            if isinstance(value, dict):
                wanted_state[key].update(value)
            else:
                wanted_state[key] = value
        if original_state == wanted_state:
            return True
        # apply the changes
        try:
            response = await self.client.room_put_state(
                room_id, state_key, wanted_state
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(
                f"Failed to change {state_label} in room ({room_label}): {exc}"
            )
            return False
        else:
            if isinstance(response, nio.responses.RoomPutStateResponse):
                return True
            else:
                logger.warning(
                    f"Refused to change {state_label} in room ({room_label}): {response}"
                )
                return False

    async def send_invitations_to_group_members(self, group, gestalten=None):
        """Send invitations to the rooms of group to all members that were not yet invited

        Optionally these invitations may be limited to a set of gestalt objects.
        """
        for room in MatrixChatGroupRoom.objects.filter(group=group):
            invited_members = [
                invite.gestalt.id
                for invite in room.invitations.distinct("gestalt").select_related(
                    "gestalt"
                )
            ]
            if gestalten is None:
                invitees = group.members.exclude(id__in=invited_members)
            else:
                invitees = [
                    gestalt
                    for gestalt in gestalten
                    if gestalt.id not in invited_members
                ]
            for gestalt in invitees:
                if self.invite_into_room(room.room_id, gestalt, str(room)):
                    yield room, gestalt

    async def invite_into_room(self, room_id: str, gestalt, room_label: str) -> bool:
        gestalt_matrix_id = MatrixChatGestaltSettings.get_matrix_id(gestalt)
        try:
            result = await self.client.room_invite(room_id, gestalt_matrix_id)
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to invite {gestalt} into {room_label}: {exc}")
            return False
        else:
            if isinstance(result, nio.responses.RoomInviteResponse):
                return True
            elif isinstance(result, nio.responses.RoomInviteError) and (
                result.status_code == "M_FORBIDDEN"
            ):
                # "forbidden" indicates that the invitee is already in the room
                return True
            else:
                logger.warning(
                    f"Invite request for {gestalt} into {room_label} was rejected: {result}"
                )
                return False

    async def kick_gestalt_from_group_rooms(self, group, gestalt, reason=None):
        gestalt_matrix_id = MatrixChatGestaltSettings.get_matrix_id(gestalt)
        for room in MatrixChatGroupRoom.objects.filter(group=group):
            try:
                result = await self.client.room_kick(
                    room.room_id, gestalt_matrix_id, reason=reason
                )
            except nio.exceptions.ProtocolError as exc:
                logger.warning(f"Failed to kick {gestalt} from {room}: {exc}")
            else:
                if isinstance(result, nio.responses.RoomKickResponse) or (
                    isinstance(result, nio.responses.RoomKickError)
                    and (result.status_code == "M_FORBIDDEN")
                ):
                    # "forbidden" indicates that we were not a member of the room.
                    # Discard invitations, anyway.
                    MatrixChatGroupRoomInvitations.objects.filter(
                        room=room, gestalt=gestalt
                    ).delete()
                else:
                    logger.warning(
                        f"Kick request for {gestalt} out of {room} was rejected: {result}"
                    )

    async def update_statistics(self):
        for room in MatrixChatGroupRoom.objects.all():
            await self.update_room_statistics(room)

    async def update_room_statistics(self, room=None):
        statistics = room.get_statistics()
        try:
            response = await self.client.joined_members(room.room_id)
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to retrieve message count from {room}: {exc}")
        else:
            if isinstance(response, nio.responses.JoinedMembersResponse):
                # the grouprise bot does not count
                statistics["members_count"] = len(response.members) - 1
            else:
                logger.warning(
                    f"Retrieval of members count from {room} was rejected: {response}"
                )
        try:
            response = await self.client.room_messages(
                room.room_id,
                start="",
                limit=1,
                message_filter={
                    "not_senders": [self.bot_matrix_id],
                    "types": ["m.room.message"],
                },
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to retrieve message count from {room}: {exc}")
        else:
            if isinstance(response, nio.responses.RoomMessagesResponse):
                if response.chunk:
                    msg = response.chunk[0]
                    # Matrix uses milliseconds for timestamps
                    statistics["last_message_timestamp"] = msg.server_timestamp / 1000
            else:
                logger.warning(
                    f"Retrieval of message count from {room} was rejected: {response}"
                )
        room.set_statistics(statistics)
        room.save()


class MatrixDummyServer:
    def __init__(self):
        self._rooms = None

    @property
    def rooms(self):
        if self._rooms is None:
            # initialize the room dictionary based on the state of the database
            self._rooms = {}
            for group_room in MatrixChatGroupRoom.objects.all():
                room_label = "Group '{}' ({})".format(
                    group_room.group, "private" if group_room.is_private else "public"
                )
                room = MatrixDummyRoom(group_room.room_id, room_label)
                for membership in group_room.group.memberships.all():
                    gestalt = membership.member
                    try:
                        room.members.add(gestalt.matrix_chat_settings.matrix_id)
                    except ObjectDoesNotExist:
                        pass
                self._rooms[room.room_id] = room
            for setting in get_matrix_notification_room_queryset():
                room_id = setting.value
                room_label = f"Gestalt '{setting.gestalt}'"
                self._rooms[room_id] = MatrixDummyRoom(room_id, room_label)
        return self._rooms


class MatrixDummyRoom:
    def __init__(self, room_id, room_label=None):
        self.state = {}
        self.members = set()
        self.sent_messages_count = 0
        self.room_id = room_id
        self.label = room_id if room_label is None else room_label


def room_resolver(response_class):
    """resolve the room based on the first parameter of the decorated function"""

    def _inner(func):
        @functools.wraps(func)
        async def _wrapped_func(self, room_id, *args, **kwargs):
            try:
                room = self.server.rooms[room_id]
            except KeyError:
                return response_class("Room does not exist")
            else:
                return await func(self, room, *args, **kwargs)

        return _wrapped_func

    return _inner


class MatrixConsoleClient:

    # the server is assigned once during module loading as a class attribute (as a singleton)
    server = None

    def __init__(self, stream=None):
        self.logged_in = True
        self._stream = sys.stdout if stream is None else stream

    def _log(self, message):
        self._stream.write(message + "\n")

    async def sync(self, set_presence=None, since=None):
        pass

    async def close(self):
        self.logged_in = False

    @staticmethod
    def _get_event_id():
        return "".join(random.choices(string.ascii_letters, k=16))

    async def _send(self, response_class, *args, **kwargs):
        return response_class()

    @room_resolver(nio.responses.RoomSendError)
    async def room_send(self, room, event_type, msg):
        room.sent_messages_count += 1
        self._log(f"Sending Matrix Message ({event_type} / {msg['msgtype']}):")
        self._log(f"    Recipient: {room.label}")
        self._log(f"    Content: {msg['body']}")
        self._log("")
        return nio.responses.RoomSendResponse(self._get_event_id(), room.room_id)

    async def room_create(self, name, topic, preset, visibility):
        room_id = "!" + "".join(random.choices(string.ascii_letters, k=18))
        if room_id in self.server.rooms:
            return nio.responses.RoomCreateError("Room already exists")
        else:
            self._log(f"Creating room: {room_id}")
            self.server.rooms[room_id] = MatrixDummyRoom(room_id)
            return nio.responses.RoomCreateResponse(room_id)

    @room_resolver(nio.responses.RoomGetStateError)
    async def room_get_state(self, room):
        return copy.deepcopy(room.state)

    @room_resolver(nio.responses.RoomPutStateError)
    async def room_put_state(self, room, state_key, wanted_state):
        self._log(
            f"Changing state of room '{room.label}' ({state_key}): {wanted_state}"
        )
        room.state[state_key] = copy.deepcopy(wanted_state)

    @room_resolver(nio.responses.RoomInviteError)
    async def room_invite(self, room, invitee_id):
        if invitee_id in room.members:
            return nio.responses.RoomInviteError(
                "Is already member of room", status_code="M_FORBIDDEN"
            )
        else:
            self._log(f"Inviting {invitee_id} to room: {room.label}")
            room.members.add(invitee_id)
            return nio.responses.RoomInviteResponse()

    @room_resolver(nio.responses.RoomKickError)
    async def room_kick(self, room, kicked_id, reason=None):
        self._log(f"Kicking {kicked_id} from room: {room.label}")
        room.members.remove(kicked_id)
        return nio.responses.RoomKickResponse()

    @room_resolver(nio.responses.JoinedMembersError)
    async def joined_members(self, room):
        members = list(room.members)
        return nio.responses.JoinedMembersResult(members, room.room_id)

    @room_resolver(nio.responses.RoomMessagesError)
    async def room_messages(self, room, *args, **kwargs):
        events = [
            nio.events.room_events.Event(
                source={},
                event_id=self._get_event_id(),
                sender="@someone:example.org",
                server_timestamp=time.time() * 1000,
                decrypted=False,
                verified=True,
                sender_key=None,
                session_id=None,
                transaction_id=None,
            ),
        ]
        return nio.responses.RoomMessagesResponse(chunks=events)


# use a singleton for the server state
MatrixConsoleClient.server = MatrixDummyServer()
