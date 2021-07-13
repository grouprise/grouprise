import copy
import logging

import markdown
import nio

from grouprise.core.templatetags.defaultfilters import full_url
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)
from .settings import MATRIX_SETTINGS


logger = logging.getLogger(__name__)


class MatrixError(Exception):
    """ an error occurred while communicating with the matrix server """


class MatrixClient(nio.AsyncClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_event_callback(self.cb_autojoin_room, nio.InviteEvent)

    async def cb_autojoin_room(self, room: nio.MatrixRoom, event: nio.InviteEvent):
        await self.join(room.room_id)


class MatrixBot:
    def __init__(self):
        matrix_url = f"https://{MATRIX_SETTINGS.DOMAIN}"
        self.bot_matrix_id = f"@{MATRIX_SETTINGS.BOT_USERNAME}:{MATRIX_SETTINGS.DOMAIN}"
        logger.info(f"Connecting to {matrix_url} as '{MATRIX_SETTINGS.BOT_USERNAME}'")
        self.client = MatrixClient(matrix_url, self.bot_matrix_id)
        # maybe we should use "self.client.login()" instead?
        self.client.access_token = MATRIX_SETTINGS.BOT_ACCESS_TOKEN

    async def sync(self, set_presence="online"):
        sync_result = await self.client.sync(set_presence=set_presence)
        if isinstance(sync_result, nio.responses.SyncError):
            raise MatrixError(
                f"Failed to synchronize state with homeserver: {sync_result}"
            )
        if not self.client.logged_in:
            raise MatrixError(
                "Failed to login. There is a problem with the matrix server or the configured "
                "account settings are invalid."
            )

    async def __aenter__(self):
        await self.sync()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.close()
        return False

    async def send_text(self, room, body, msgtype="m.notice", parser="markdown"):
        msg = {"body": body, "msgtype": msgtype}
        if parser == "markdown":
            msg["format"] = "org.matrix.custom.html"
            msg["formatted_body"] = markdown.markdown(body)
        try:
            response = await self.client.room_send(room.room_id, "m.room.message", msg)
        except nio.exceptions.ProtocolError as exc:
            raise MatrixError(f"Failed to send message: {exc}")
        else:
            if not isinstance(response, nio.responses.RoomSendResponse):
                raise MatrixError(f"Failed to send message: {response}")

    async def synchronize_rooms_of_group(self, group):
        """ create rooms for the group and synchronize their avatar with the grouprise avatar """
        for is_private in (False, True):
            try:
                room, created = await self._get_or_create_room(group, is_private)
            except MatrixError as exc:
                logger.error(f"Failed to create room: {exc}")
            else:
                if created:
                    yield room
                await self.configure_room(room)

    def _get_group_room_name_local(self, group, is_private):
        return (group.slug or group.name) + ("-private" if is_private else "")

    async def _get_or_create_room(self, group, is_private):
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
        group_name_local = self._get_group_room_name_local(group, is_private)
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
            raise MatrixError(f"Failed to create room '{group_name_local}': {exc}")
        if not isinstance(response, nio.responses.RoomCreateResponse):
            raise MatrixError(
                f"Create room requested for '{group_name_local}' was rejected: {response}"
            )
        # store the room
        room = MatrixChatGroupRoom.objects.create(
            group=group, is_private=is_private, room_id=response.room_id
        )
        # respond with success, even though the alias assignment may have failed
        return room, True

    async def configure_room(self, room):
        group_name_local = self._get_group_room_name_local(room.group, room.is_private)
        room_alias = f"#{group_name_local}:{MATRIX_SETTINGS.DOMAIN}"
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
        if not await self._change_room_power_state(room, {"users_default": 50}):
            logger.warning(
                f"Failed to raise default role for new members ({room_alias})"
            )

    async def _change_room_power_state(self, room, changes):
        """configure the power levels in a room

        The procedure is a bit complicated, since we need to send a full state dictionary.
        Thus we retrieve the current state first and merge it with the wanted changes.
        The result is sent to the server (if it differs from the current state).

        Specification: https://matrix.org/docs/spec/client_server/latest#id253
        """
        # retrieve the current state
        try:
            response = await self.client.room_get_state(room.room_id)
            failure_reason = None
        except nio.exceptions.ProtocolError as exc:
            response = None
            failure_reason = exc
        if not isinstance(response, nio.responses.RoomGetStateResponse):
            logger.warning(f"Failed to get room state ({room}): {failure_reason}")
            return False
        original_state = [
            event for event in response.events if event["type"] == "m.room.power_levels"
        ][0]["content"]
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
                room.room_id,
                "m.room.power_levels",
                wanted_state,
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to change power levels in room ({room}): {exc}")
            return False
        else:
            if isinstance(response, nio.responses.RoomPutStateResponse):
                return True
            else:
                logger.warning(
                    f"Refused to change power levels in room ({room}): {response}"
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
                gestalt_matrix_id = MatrixChatGestaltSettings.get_matrix_id(gestalt)
                try:
                    result = await self.client.room_invite(
                        room.room_id, gestalt_matrix_id
                    )
                except nio.exceptions.ProtocolError as exc:
                    logger.warning(f"Failed to invite {gestalt} into {room}: {exc}")
                else:
                    if isinstance(result, nio.responses.RoomInviteResponse) or (
                        isinstance(result, nio.responses.RoomInviteError)
                        and (result.status_code == "M_FORBIDDEN")
                    ):
                        # "forbidden" is used for "is already in the room" - we remember this
                        MatrixChatGroupRoomInvitations.objects.create(
                            room=room, gestalt=gestalt
                        )
                        yield room, gestalt
                    else:
                        logger.warning(
                            f"Invite request for {gestalt} into {room} was rejected: {result}"
                        )

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
