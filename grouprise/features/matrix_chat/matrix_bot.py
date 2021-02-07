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


class MatrixBot:
    def __init__(self):
        matrix_url = f"https://{MATRIX_SETTINGS.DOMAIN}"
        bot_matrix_id = f"@{MATRIX_SETTINGS.BOT_USERNAME}:{MATRIX_SETTINGS.DOMAIN}"
        logger.info(f"Connecting to {matrix_url} as '{MATRIX_SETTINGS.BOT_USERNAME}'")
        self.client = nio.AsyncClient(matrix_url, bot_matrix_id)
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
                logger.error(f"Failed to synchronize room: {exc}")
                continue
            if created:
                yield room

    async def _get_or_create_room(self, group, is_private):
        try:
            room = MatrixChatGroupRoom.objects.get(group=group, is_private=is_private)
            return room, False
        except MatrixChatGroupRoom.DoesNotExist:
            pass
        # the room does not exist: we need to create it
        group_url = full_url(group.get_absolute_url())
        if is_private:
            suffix = "-private"
            room_title = "{} (private)".format(group.name)
            room_description = "{} - members only".format(group_url)
        else:
            suffix = ""
            room_title = group.name
            room_description = group_url
        group_name_local = (group.slug or group.name) + suffix
        preset = (
            nio.api.RoomPreset.private_chat
            if is_private
            else nio.api.RoomPreset.public_chat
        )
        try:
            response = await self.client.room_create(
                name=room_title, topic=room_description, preset=preset
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
        # try to attach the canonical alias (optional)
        room_alias = f"#{group_name_local}:{MATRIX_SETTINGS.DOMAIN}"
        try:
            response = await self.client.room_put_state(
                room.room_id,
                "m.room.canonical_alias",
                {"alias": room_alias},
            )
        except nio.exceptions.ProtocolError as exc:
            logger.warning(f"Failed to assign alias ({room_alias}) to room: {exc}")
        else:
            if not isinstance(response, nio.responses.RoomPutStateResponse):
                logger.warning(
                    f"Refused to assign alias ({room_alias}) to room: {response}"
                )
        # respond with success, even though the alias assignment may have failed
        return room, True

    async def send_invitations_to_group_members(self, group):
        for room in MatrixChatGroupRoom.objects.filter(group=group):
            invited_members = [
                invite.gestalt.id
                for invite in room.invitations.distinct("gestalt").select_related(
                    "gestalt"
                )
            ]
            for gestalt in group.members.exclude(id__in=invited_members):
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
