from django.urls import reverse

from grouprise.core import tests
from grouprise.core.matrix import get_dummy_matrix_server, MatrixDummyRoom
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS
from grouprise.features.matrix_chat.utils import (
    get_gestalt_matrix_notification_room,
    create_public_room,
)
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin


class MatrixRoomTracker:
    def __init__(self, room: MatrixDummyRoom):
        self._room_id = room.room_id
        self._rooms_dict = get_dummy_matrix_server().rooms
        self._previous_messages_count = None
        self._previous_members_count = None

    def __enter__(self):
        self._previous_members_count = len(self.room.members)
        self._previous_messages_count = self.room.sent_messages_count
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    # The room instances seem to get *replaced* instead of modified in case of changes.
    # Thus, we grab a fresh reference whenever we need to access a room.
    @property
    def room(self):
        return self._rooms_dict[self._room_id]

    @property
    def members_count(self):
        return len(self.room.members) - self._previous_members_count

    @property
    def messages_count(self):
        return self.room.sent_messages_count - self._previous_messages_count


class MatrixChatMixin:

    matrix_server = get_dummy_matrix_server()

    @classmethod
    def get_gestalt_room(cls, gestalt: Gestalt):
        room_id = get_gestalt_matrix_notification_room(gestalt)
        return cls.matrix_server.rooms[room_id]

    @classmethod
    def get_group_rooms(cls, group: Group):
        private_room = None
        public_room = None
        for room in group.matrix_rooms.all():
            matrix_room = cls.matrix_server.rooms[room.room_id]
            if room.is_private:
                private_room = matrix_room
            else:
                public_room = matrix_room
        return private_room, public_room

    @classmethod
    def get_public_listener_room(cls):
        room_id = MATRIX_SETTINGS.PUBLIC_LISTENER_ROOMS[0]
        return cls.matrix_server.rooms[room_id]

    @classmethod
    def setUpTestData(cls):
        cls.matrix_server.reset()
        super().setUpTestData()


class MatrixRoomCreation(MatrixChatMixin, AuthenticatedMemberMixin, tests.Test):
    def test_room_creation(self):
        """Matrix rooms are created whenever a group is created"""
        room_count_before = len(self.matrix_server.rooms)
        self.client.post(self.get_url("group-create"), {"name": "Test"})
        self.assertEqual(len(self.matrix_server.rooms), room_count_before + 2)


class MatrixGroupNotifications(MatrixChatMixin, AuthenticatedMemberMixin, tests.Test):
    def _create_article(self, public):
        self.client.post(
            reverse("create-group-article", args=(self.group.slug,)),
            {"title": "Test", "text": "Test", "public": public},
        )

    def test_private_only(self):
        """content announcements are sent to the private Matrix room of a group"""
        private_room, public_room = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_room) as private_tracker:
            with MatrixRoomTracker(public_room) as public_tracker:
                self._create_article(public=False)
                self.assertEqual(public_tracker.messages_count, 0)
                self.assertEqual(private_tracker.messages_count, 1)

    def test_public(self):
        """content announcements are sent to the all Matrix rooms of a group"""
        private_room, public_room = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_room) as private_tracker:
            with MatrixRoomTracker(public_room) as public_tracker:
                self._create_article(public=True)
                self.assertEqual(public_tracker.messages_count, 1)
                self.assertEqual(private_tracker.messages_count, 1)

    def test_public_listener_room_receives_notification_for_public_message(self):
        with MATRIX_SETTINGS.temporary_override(
            PUBLIC_LISTENER_ROOMS=[create_public_room()]
        ):
            room = self.get_public_listener_room()
            with MatrixRoomTracker(room) as tracker:
                self._create_article(public=True)
                self.assertEqual(tracker.messages_count, 1)

    def test_public_listener_room_does_not_receive_notification_for_private_message(
        self,
    ):
        with MATRIX_SETTINGS.temporary_override(
            PUBLIC_LISTENER_ROOMS=[create_public_room()]
        ):
            room = self.get_public_listener_room()
            with MatrixRoomTracker(room) as tracker:
                self._create_article(public=False)
                self.assertEqual(tracker.messages_count, 0)
