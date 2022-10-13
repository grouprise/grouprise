import copy
import functools
import logging
import random
import string
import sys
import time
from typing import Callable

import markdown
import nio

from django.core.cache import cache

from grouprise.settings_loader import MatrixBackend


logger = logging.getLogger(__name__)


# source: https://matrix.org/docs/guides/moderation#power-levels
MATRIX_ROOM_POWER_LEVEL_MINIMAL = 0
MATRIX_ROOM_POWER_LEVEL_MODERATOR = 50


class MatrixError(Exception):
    """an error occurred while communicating with the matrix server"""


def get_matrix_client(server_url, user_id, access_token, backend=MatrixBackend.NIO):
    logger.info("Connecting to %s as '%s'", server_url, user_id)
    if backend == MatrixBackend.NIO:
        client = nio.AsyncClient(server_url, user_id)
        # maybe we should use "self.client.login()" instead?
    elif backend == MatrixBackend.CONSOLE:
        client = MatrixConsoleClient()
        client.homeserver = server_url
        client.user_id = user_id
    else:
        raise NotImplementedError(
            f"The selected Matrix backend is not supported: {backend}"
        )
    client.access_token = access_token
    return client


class MatrixBaseBot:
    def __init__(self, server_url, user_id, access_token, backend=MatrixBackend.NIO):
        self.client = get_matrix_client(
            server_url, user_id, access_token, backend=backend
        )

    async def sync(self, set_presence="online", since=None, update_period=None):
        """synchronize the bot state with the server state

        If "update_period" is specified, then the function is running forever and
        polls for new events.  The period defines the maximum duration of a request,
        even if no events are received.  Callbacks are executed immediately anyway.
        """
        sync_token_cache_key = ".".join(
            ["matrix_chat", "sync_token", self.client.homeserver, self.client.user_id]
        )
        if since is None:
            since = cache.get(sync_token_cache_key)
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
        cache.set(sync_token_cache_key, sync_result.next_batch, 24 * 3600)
        return sync_result

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
                raise MatrixError(
                    f"Failed to send message due to rejection: {response}"
                )


class MatrixDummyServer:
    def __init__(self):
        self.rooms = {}

    def reset(self):
        self.rooms.clear()


class MatrixDummyRoom:
    def __init__(self, room_id, room_label=None):
        self.state = {"m.room.power_levels": {"users": {}}}
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
    # the output target can be overwritten (e.g. during tests)
    output_stream = sys.stdout

    def __init__(self):
        self.logged_in = True

    def _log(self, message):
        if self.output_stream is not None:
            self.output_stream.write(message + "\n")

    async def sync(self, set_presence=None, since=None):
        return nio.responses.SyncResponse(
            next_batch=str(int(time.time())),
            rooms={},
            device_key_count=0,
            device_list=None,
            to_device_events=[],
            presence_events=[],
        )

    async def sync_forever(self, *args, **kwargs):
        while True:
            pass

    async def close(self):
        self.logged_in = False

    def add_event_callback(
        self, func: Callable[[nio.MatrixRoom, nio.Event], None], event: nio.Event
    ):
        # just a stub: there is currently no need for the handling of events
        pass

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
        events = [{"type": key, "content": value} for key, value in room.state.items()]
        return nio.RoomGetStateResponse(events=events, room_id=room.room_id)

    @room_resolver(nio.responses.RoomPutStateError)
    async def room_put_state(self, room, state_key, wanted_state):
        self._log(
            f"Changing state of room '{room.label}' ({state_key}): {wanted_state}"
        )
        room.state[state_key] = copy.deepcopy(wanted_state)
        return nio.RoomPutStateResponse(event_id=int(time.time()), room_id=room.room_id)

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


def get_dummy_matrix_server():
    return MatrixConsoleClient.server
