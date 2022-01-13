import logging
import os
import re

import markdown
import nio

from grouprise.features.matrix_chat.matrix_bot import MatrixBot

from .commands import MatrixCommander
from .settings import MATRIX_COMMANDER_SETTINGS

logger = logging.getLogger(__name__)


class CommanderBot(MatrixBot):
    def __init__(self, command_prefix=None):
        self._commander = MatrixCommander()
        self.bot_id = MATRIX_COMMANDER_SETTINGS.BOT_ID
        bot_access_token = MATRIX_COMMANDER_SETTINGS.BOT_ACCESS_TOKEN
        domain = self.bot_id.split(":")[-1]
        matrix_url = f"https://{domain}"
        self.client = nio.AsyncClient(matrix_url, self.bot_id)
        self.client.access_token = bot_access_token
        self.client.add_event_callback(self.cb_autojoin_admin_rooms, nio.InviteEvent)
        self.client.add_event_callback(self.handle_encrypted_message, nio.MegolmEvent)
        self.client.add_event_callback(self.handle_message, nio.RoomMessageText)
        if command_prefix is None:
            local_part = re.escape(self.bot_id.split(":")[0].lstrip("@"))
            hostname = re.escape(self.bot_id.split(":", 1)[1])
            self._prefix_regex = re.compile(
                fr"^(@?{local_part}(:{hostname})?:?|!grouprise)$"
            )
        else:
            escaped = re.escape(command_prefix)
            self._prefix_regex = re.compile(fr"^{escaped}$")
        self._ignore_messages = False

    def is_admin_room(self, room: nio.MatrixRoom):
        return room.room_id in MATRIX_COMMANDER_SETTINGS.ADMIN_ROOMS

    async def cb_autojoin_admin_rooms(
        self, room: nio.MatrixRoom, event: nio.InviteEvent
    ):
        if self.is_admin_room(room):
            logger.info("Joining administration room: %s", room.room_id)
            await self.client.join(room.room_id)
        else:
            logger.info("Rejecting invitation for unknown room: %s", room.room_id)
            await self.client.room_leave(room.room_id)

    async def send_text(
        self, room: nio.MatrixRoom, body: str, msgtype="m.notice", parser="markdown"
    ):
        msg = {"body": body, "msgtype": msgtype}
        if parser == "markdown":
            msg["formatted"] = markdown.markdown(body)
            msg["formatted_body"] = "org.matrix.custom.html"
        try:
            response = await self.client.room_send(room.room_id, "m.room.message", msg)
        except nio.exceptions.ProtocolError as exc:
            logger.warning("Failed to send message: %s", exc)
        else:
            if not isinstance(response, nio.responses.RoomSendResponse):
                logger.warning("Failed to send message due to rejection: %s", response)

    async def serve_forever(self):
        # discard old messages during an initial sync
        self._ignore_messages = True
        await self.sync()
        logger.info(
            "Bot has logged in successfully and is waiting for requests: %s",
            self.bot_id,
        )
        # process all further (new) messages
        self._ignore_messages = False
        await self.sync(set_presence="online", update_period=30)
        await self.close()

    async def handle_message(self, room: nio.MatrixRoom, event: nio.RoomMessageText):
        if self._ignore_messages:
            logger.debug("Ignoring old message: %s", event)
        elif not self.is_admin_room(room):
            logger.warning("Ignoring request from a non-admin room: %s", room)
            await self.send_text(
                room,
                f"Ignoring request, since this room ({room.room_id}) is not"
                f" configured in 'matrix_commander.admin_rooms'.",
            )
        else:
            message = event.body
            tokens = message.split(maxsplit=1)
            if len(tokens) < 2:
                return
            prefix, remainder = tokens
            if self._prefix_regex.match(prefix):
                logger.info("Processing incoming message: %s", remainder[:60])
                response = os.linesep.join(self._commander.process_command(remainder))
                await self.send_text(room, response)

    async def handle_encrypted_message(
        self, room: nio.MatrixRoom, event: nio.MegolmEvent
    ):
        logger.info("Received encrypted message from room: %s", room.name)
        response = os.linesep.join(
            [
                'Sorry, grouprise\'s "matrix-commander" bot does not support encryption.',
                "You should not not invite this bot to encrypted rooms.",
            ]
        )
        await self.send_text(room, response)
