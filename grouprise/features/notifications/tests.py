from django.core import mail
from django.test import TestCase
from django.urls import reverse

from grouprise.features.articles.tests import GroupArticleMixin
from grouprise.features.matrix_chat.tests import MatrixChatMixin, MatrixRoomTracker
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin


class AuthenticatedMemberArticleTestCase(
    MatrixChatMixin, GroupArticleMixin, AuthenticatedMemberMixin, TestCase
):
    def test_receives_email_notification_upon_content_creation(self):
        mail.outbox.clear()
        self._create_article()
        self.assertEqual(len(mail.outbox), 1)

    def test_receives_email_notification_upon_contribution_creation(self):
        mail.outbox.clear()
        self._create_comment()
        self.assertEqual(len(mail.outbox), 1)

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
