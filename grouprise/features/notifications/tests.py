from unittest import skip

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from grouprise.features.articles.tests import GroupArticleMixin
from grouprise.features.conversations.tests import GestaltConversationMixin
from grouprise.features.matrix_chat.tests import MatrixChatMixin, MatrixRoomTracker
from grouprise.features.memberships.test_mixins import (
    MemberMixin,
    OtherMemberMixin,
)


class AuthenticatedMemberArticleTestCase(
    MatrixChatMixin,
    GroupArticleMixin,
    MemberMixin,
    OtherMemberMixin,
    TestCase,
):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.other_gestalt.user)

    def test_receives_builtin_notification_upon_content_creation(self):
        notification_count = self.gestalt.notifications.count()
        self._create_article()
        self.assertEqual(self.gestalt.notifications.count(), notification_count + 1)

    def test_receives_builtin_notification_upon_contribution_creation(self):
        notification_count = self.gestalt.notifications.count()
        self._create_comment()
        self.assertEqual(self.gestalt.notifications.count(), notification_count + 1)

    def test_receives_email_notification_upon_content_creation(self):
        mail.outbox.clear()
        self._create_article()
        self.assertEqual(len(mail.outbox), 2)

    def test_receives_email_notification_upon_contribution_creation(self):
        mail.outbox.clear()
        self._create_comment()
        self.assertEqual(len(mail.outbox), 2)

    def test_receives_matrix_notification_upon_content_creation(self):
        private_room, _ = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_room) as room_tracker:
            self._create_article()
            self.assertEqual(room_tracker.messages_count, 1)

    def test_receives_matrix_notification_upon_contribution_creation(self):
        private_room, _ = self.get_group_rooms(self.group)
        with MatrixRoomTracker(private_room) as room_tracker:
            self._create_comment()
            self.assertEqual(room_tracker.messages_count, 1)

    def _create_article(self):
        url = reverse("create-group-article", args=[self.group.slug])
        self.client.post(url, {"title": "Test", "text": "Test"})

    def _create_comment(self):
        url = reverse(
            "content", args=[self.association.entity.slug, self.association.slug]
        )
        self.client.post(url, {"text": "Test Comment"})


class OtherAuthenticatedConversationTestCase(
    MatrixChatMixin, GestaltConversationMixin, TestCase
):
    def setUp(self) -> None:
        super().setUp()
        self.client.force_login(self.other_gestalt.user)

    def test_receives_matrix_notification_upon_gestalt_conversation_reply(self):
        gestalt_room = self.get_gestalt_room(self.gestalt)
        with MatrixRoomTracker(gestalt_room) as room_tracker:
            self._create_reply()
            self.assertEqual(room_tracker.messages_count, 1)

    def _create_reply(self):
        url = reverse("conversation", args=[self.association.pk])
        self.client.post(url, {"text": "Test Reply"})
