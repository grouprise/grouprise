from typing import Iterable
import copy
import logging

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import nio

from grouprise.core.matrix import (
    MatrixBaseBot,
    MatrixDummyRoom,
    MatrixError,
    MATRIX_ROOM_POWER_LEVEL_MODERATOR,
)
from grouprise.core.templatetags.defaultfilters import full_url
from grouprise.features.gestalten.models import GestaltSetting
from grouprise.settings_loader import MatrixBackend

from . import (
    GESTALT_SETTINGS_CATEGORY_MATRIX,
    GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
)
from .models import (
    MatrixChatGestaltSettings,
    MatrixChatGroupRoom,
    MatrixChatGroupRoomInvitations,
)
from .settings import MATRIX_SETTINGS


logger = logging.getLogger(__name__)


def get_matrix_notification_room_queryset():
    return GestaltSetting.objects.filter(
        name=GESTALT_SETTINGS_KEY_PRIVATE_NOTIFICATION_ROOM,
        category=GESTALT_SETTINGS_CATEGORY_MATRIX,
    )


def _get_group_members_matrix_addresses(group):
    return {
        MatrixChatGestaltSettings.get_matrix_id(gestalt)
        for gestalt in group.members.all()
    }


def _populate_group_rooms(server):
    """initialize the room dictionary based on the state of the database"""
    for group_room in MatrixChatGroupRoom.objects.all():
        if group_room.room_id not in server.rooms:
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
            # the bot itself is in the room, too
            room.members.add(server.bot_matrix_id)
            server.rooms[room.room_id] = room
    for setting in get_matrix_notification_room_queryset():
        room_id = setting.value
        if room_id not in server.rooms:
            room_label = f"Gestalt '{setting.gestalt}'"
            server.rooms[room_id] = MatrixDummyRoom(room_id, room_label)


class ChatBot(MatrixBaseBot):
    def __init__(self):
        matrix_url = f"https://{MATRIX_SETTINGS.DOMAIN}"
        self.bot_matrix_id = f"@{MATRIX_SETTINGS.BOT_USERNAME}:{MATRIX_SETTINGS.DOMAIN}"
        access_token = MATRIX_SETTINGS.BOT_ACCESS_TOKEN
        self._backend = MATRIX_SETTINGS.BACKEND
        super().__init__(
            matrix_url, self.bot_matrix_id, access_token, backend=self._backend
        )

        async def join_and_configure_group_room_after_invite(
            room: nio.MatrixRoom, event: nio.InviteEvent
        ):
            await self.client.join(room.room_id)
            try:
                room_object = MatrixChatGroupRoom.objects.get(room_id=room.room_id)
            except MatrixChatGroupRoom.DoesNotExist:
                pass
            else:
                await self.configure_group_room(room_object)

        self.client.add_event_callback(
            join_and_configure_group_room_after_invite, nio.InviteEvent
        )

    async def __aenter__(self):
        if (self._backend == MatrixBackend.CONSOLE) and not self.client.server.rooms:
            await sync_to_async(_populate_group_rooms)(self.client.server)
        return await super().__aenter__()

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
            room = await sync_to_async(MatrixChatGroupRoom.objects.get)(
                group=group, is_private=is_private
            )
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
        room_id = await self.create_room(room_title, room_description, is_private)
        # store the room
        room = await sync_to_async(MatrixChatGroupRoom.objects.create)(
            group=group, is_private=is_private, room_id=room_id
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
            # We cannot detect the state of an alias already existing.
            # Thus, we need to parse the message.
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
        # try to change default role of new members
        # Private rooms:
        #    - Only group members or explicitly invited people are inside.
        #    - Everyone has the moderator level.
        # Public rooms:
        #    - All group members are raised to moderator level.
        #    - Anyone who joined on his own (without being a group member) has the standard level.
        default_power_level = (
            MATRIX_ROOM_POWER_LEVEL_MODERATOR if room.is_private else 0
        )
        if not await self._change_room_state(
            room.room_id,
            {"users_default": default_power_level},
            "m.room.power_levels",
            room_label=str(room),
        ):
            logger.warning(
                "Failed to change default role for new members (%s)", room_alias
            )
        # try to raise power levels for group members in public rooms
        if not room.is_private:
            member_addresses = await sync_to_async(_get_group_members_matrix_addresses)(
                room.group
            )
            await self.raise_room_members_power_levels(
                room.room_id,
                member_addresses,
                MATRIX_ROOM_POWER_LEVEL_MODERATOR,
                str(room),
            )

    async def create_room(self, room_title, room_description, is_private: bool):
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
        Thus, we retrieve the current state first and merge it with the wanted changes.
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

        def get_rooms(group):
            return list(MatrixChatGroupRoom.objects.filter(group=group))

        def get_room_invitations(room):
            return list(room.invitations.select_related("gestalt"))

        def get_group_members_with_exceptions(group, ignored_members):
            return list(group.members.exclude(id__in=invited_members))

        for room in await sync_to_async(get_rooms)(group):
            invited_members = {
                invite.gestalt.id
                for invite in await sync_to_async(get_room_invitations)(room)
            }
            if gestalten is None:
                invitees = await sync_to_async(get_group_members_with_exceptions)(
                    group, invited_members
                )
            else:
                invitees = [
                    gestalt
                    for gestalt in gestalten
                    if gestalt.id not in invited_members
                ]
            for gestalt in invitees:
                room_label = await sync_to_async(str)(room)
                try:
                    await self.invite_into_room(room.room_id, gestalt, room_label)
                except MatrixError as exc:
                    logger.warning(str(exc))
                else:
                    yield room, gestalt

    async def raise_room_members_power_levels(
        self,
        room_id: str,
        matrix_addresses: Iterable[str],
        new_level: int,
        room_label: str,
    ):
        """raise the power levels of the given matrix addresses in a room

        The power level of each matrix address is changed only, if its current level is lower than
        the new target level.
        Addresses without a specific level (e.g. they were invited, but did not join, yet) also
        receive their future power level, which will become active as soon as they join.
        """
        response = await self._get_room_state(room_id, "m.room.power_levels")
        if not response:
            logger.warning(
                "Failed to retrieve current power levels for group members (%s)",
                room_label,
            )
            return
        user_power_levels = response["users"]
        for matrix_address in matrix_addresses:
            if user_power_levels.get(matrix_address, -1) < new_level:
                user_power_levels[matrix_address] = new_level
        if not await self._change_room_state(
            room_id,
            {"users": user_power_levels},
            "m.room.power_levels",
            room_label=room_label,
        ):
            logger.warning(
                "Failed to raise power levels for group members (%s)", room_label
            )

    async def invite_into_room(self, room_id: str, gestalt, room_label: str) -> None:
        gestalt_matrix_id = await sync_to_async(
            MatrixChatGestaltSettings.get_matrix_id
        )(gestalt)
        try:
            result = await self.client.room_invite(room_id, gestalt_matrix_id)
        except nio.exceptions.ProtocolError as exc:
            raise MatrixError(
                f"Failed to invite {gestalt} into {room_label}: {exc}"
            ) from exc
        else:
            if isinstance(result, nio.responses.RoomInviteResponse):
                pass
            elif isinstance(result, nio.responses.RoomInviteError) and (
                result.status_code == "M_FORBIDDEN"
            ):
                # "forbidden" indicates that the invitee is already in the room
                pass
            else:
                raise MatrixError(
                    f"Invite request for {gestalt} into {room_label} was rejected: {result}"
                )

    async def kick_gestalt_from_group_rooms(self, group, gestalt, reason=None):
        def get_group_chat_rooms(group):
            return list(MatrixChatGroupRoom.objects.filter(group=group))

        def delete_room_invitations(room, gestalt):
            MatrixChatGroupRoomInvitations.objects.filter(
                room=room, gestalt=gestalt
            ).delete()

        gestalt_matrix_id = await sync_to_async(
            MatrixChatGestaltSettings.get_matrix_id
        )(gestalt)
        for room in await sync_to_async(get_group_chat_rooms)(group):
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
                    await sync_to_async(delete_room_invitations)(room, gestalt)
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
