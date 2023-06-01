from django.urls import reverse

from grouprise.core import tests
from grouprise.core.matrix import get_dummy_matrix_server, MatrixDummyRoom
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.gestalten.tests.mixins import AuthenticatedMixin
from grouprise.features.groups.models import Group
from grouprise.features.groups.tests.mixins import GroupMixin
from grouprise.features.matrix_chat.settings import MATRIX_SETTINGS
from grouprise.features.matrix_chat.utils import (
    get_gestalt_matrix_notification_room,
    create_public_room,
)
from grouprise.features.memberships.models import Membership
from grouprise.features.conversations.tests import (
    AuthenticatedGestaltConversationMixin,
    AuthenticatedGroupConversationMixin,
)
from grouprise.features.memberships.test_mixins import (
    AuthenticatedMemberMixin,
    OtherMemberMixin,
)

from .models import MatrixChatGestaltSettings, MatrixChatGroupRoomInvitations
from .tasks import synchronize_matrix_rooms


class MatrixRoomTracker:
    def __init__(self, room: MatrixDummyRoom):
        self._room_id = room.room_id
        self._rooms_dict = get_dummy_matrix_server().rooms
        self._previous_invitations_count = None
        self._previous_members_count = None
        self._previous_messages_count = None

    def __enter__(self):
        self._previous_invitations_count = self.room.sent_invitations_count
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
    def invitations_count(self) -> int:
        return self.room.sent_invitations_count - self._previous_invitations_count

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
    def get_gestalt_matrix_id(cls, gestalt: Gestalt) -> str:
        return MatrixChatGestaltSettings.get_matrix_id(gestalt)

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

    def test_group_private_notification(self):
        """content announcements are sent to the private Matrix room of a group"""
        private_room, public_room = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_room) as private_tracker:
            with MatrixRoomTracker(public_room) as public_tracker:
                self._create_article(public=False)
                self.assertEqual(public_tracker.messages_count, 0)
                self.assertEqual(private_tracker.messages_count, 1)

    def test_group_public_notification(self):
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


class MatrixGroupLeave(MatrixChatMixin, AuthenticatedMemberMixin, tests.Test):
    def test_matrix_id_removed_from_group_rooms(self):
        private_room, public_room = self.get_group_rooms(self.group)
        # the member and the bot are in the rooms
        self.assertEqual(len(private_room.members), 2)
        self.assertEqual(len(public_room.members), 2)
        self.leave_group()
        # only the bot remains in the rooms
        self.assertEqual(len(private_room.members), 1)
        self.assertEqual(len(public_room.members), 1)


class MatrixGroupInvitationAfterJoin(
    MatrixChatMixin, AuthenticatedMixin, GroupMixin, tests.Test
):
    def _join_group(self) -> None:
        Membership.objects.create(
            created_by=self.gestalt, group=self.group, member=self.gestalt
        )

    def _leave_group(self) -> None:
        Membership.objects.filter(group=self.group, member=self.gestalt).delete()

    def _set_gestalt_matrix_id(self, gestalt: Gestalt, matrix_id: str) -> None:
        matrix_settings, created = MatrixChatGestaltSettings.objects.get_or_create(
            gestalt=gestalt
        )
        matrix_settings.matrix_id_override = matrix_id
        matrix_settings.save()

    def tearDown(self):
        """reset group membership, invitations and matrix IDs"""
        self.group.members.clear()
        private_room, public_room = self.get_group_rooms(self.group)
        private_room.members.clear()
        public_room.members.clear()
        MatrixChatGroupRoomInvitations.objects.filter(gestalt=self.gestalt).delete()
        MatrixChatGestaltSettings.objects.filter(gestalt=self.gestalt).delete()
        super().tearDown()

    def test_invitation_after_join(self):
        private_room, public_room = self.get_group_rooms(self.group)
        # join the public matrix room before joining the group
        public_room.members.add(self.get_gestalt_matrix_id(self.gestalt))
        with MatrixRoomTracker(private_room) as private_tracker:
            with MatrixRoomTracker(public_room) as public_tracker:
                self._join_group()
                self.assertEqual(private_tracker.invitations_count, 1)
                self.assertEqual(public_tracker.invitations_count, 0)
                self._leave_group()
                self._join_group()
                self.assertEqual(private_tracker.invitations_count, 2)
                self.assertEqual(public_tracker.invitations_count, 1)

    def test_skip_duplicate_invitation(self):
        private_room, public_room = self.get_group_rooms(self.group)
        with MatrixRoomTracker(public_room) as public_tracker:
            self._join_group()
            self.assertEqual(public_tracker.invitations_count, 1)
            # leave the room (while staying within the group)
            public_room.members.remove(self.get_gestalt_matrix_id(self.gestalt))
            # trigger periodic submission of matrix invitations
            synchronize_matrix_rooms.func()
            self.assertEqual(public_tracker.invitations_count, 1)

    def test_reinvite_after_gestalt_matrix_id_changed(self):
        private_room, public_room = self.get_group_rooms(self.group)
        # trigger the creation of the gestalt's `matrix_chat_settings` object
        with MatrixRoomTracker(private_room) as private_tracker:
            self._join_group()
            self.assertEqual(private_tracker.invitations_count, 1)
            self._set_gestalt_matrix_id(self.gestalt, "@fooby:example.org")
            self.assertEqual(private_tracker.invitations_count, 2)


class MatrixPrivateConversationNotification(
    MatrixChatMixin, AuthenticatedGestaltConversationMixin, tests.Test
):
    def test_private_chat_arrives_at_recipient(self):
        """matrix notifications are sent for private messages between two gestalts"""
        my_room = self.get_gestalt_room(self.gestalt)
        other_room = self.get_gestalt_room(self.other_gestalt)
        with MatrixRoomTracker(my_room) as my_tracker:
            with MatrixRoomTracker(other_room) as other_tracker:
                self.assertEqual(my_tracker.messages_count, 0)
                self.assertEqual(other_tracker.messages_count, 0)
                self._create_conversation_to_other()
                # only the recipients receives a notification
                self.assertEqual(my_tracker.messages_count, 0)
                self.assertEqual(other_tracker.messages_count, 1)


class MatrixGroupConversationNotification(
    MatrixChatMixin, AuthenticatedGroupConversationMixin, OtherMemberMixin, tests.Test
):
    def test_incoming_message_arrives_at_group_member(self):
        """matrix notifications are sent for messages between a user and a group"""
        gestalt_room = self.get_gestalt_room(self.gestalt)
        private_group_room, public_group_room = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_group_room) as private_tracker:
            with MatrixRoomTracker(public_group_room) as public_tracker:
                with MatrixRoomTracker(gestalt_room) as gestalt_tracker:
                    self.assertEqual(gestalt_tracker.messages_count, 0)
                    self.assertEqual(public_tracker.messages_count, 0)
                    self.assertEqual(private_tracker.messages_count, 0)
                    association = self._create_conversation_to_group()
                    # only members (private room) receive a notification
                    self.assertEqual(gestalt_tracker.messages_count, 0)
                    self.assertEqual(public_tracker.messages_count, 0)
                    self.assertEqual(private_tracker.messages_count, 1)
                    # send a reply as the "other" gestalt
                    self.client.logout()
                    self.client.force_login(self.other_gestalt.user)
                    conversation_url = self.get_url("conversation", key=association.pk)
                    self.client.post(conversation_url, {"text": "Test Reply"})
                    # members and the initial poster receive a notification
                    self.assertEqual(gestalt_tracker.messages_count, 1)
                    self.assertEqual(public_tracker.messages_count, 0)
                    self.assertEqual(private_tracker.messages_count, 2)
