from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from grouprise.core.tests import Test
from grouprise.features.articles.tests import ArticleMixin, GroupArticleMixin
from grouprise.features.associations.models import Association
from grouprise.features.conversations.models import Conversation
from grouprise.features.imports.mails import ContributionMailProcessor
from grouprise.features.gestalten.tests.mixins import OtherGestaltMixin
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin

from . import models


class ContributionMixin(ArticleMixin):
    def create_contribution(self):
        self.client.post(
            reverse(
                "content", args=[self.association.entity.slug, self.association.slug]
            ),
            {"text": "Test Comment"},
        )
        return models.Contribution.objects.get(text__text="Test Comment")

    def setUp(self):
        super().setUp()
        self.contribution = self.create_contribution()

    def mark_contribution_deleted(self):
        self.contribution.deleted = timezone.now()
        self.contribution.save()


class Delete(ContributionMixin, TestCase):
    def test_delete_contribution(self):
        delete_url = reverse(
            "delete-contribution",
            args=[
                self.association.entity.slug,
                self.association.slug,
                self.contribution.pk,
            ],
        )
        article_url = reverse(
            "content", args=[self.association.entity.slug, self.association.slug]
        )

        # article contains comment
        r = self.client.get(article_url)
        self.assertContains(r, "Test Comment")

        # find delete link on article page
        self.assertContains(r, 'href="{}"'.format(delete_url))

        # get delete confirmation page
        r = self.client.get(delete_url)
        self.assertEqual(r.status_code, 200)

        # delete comment
        r = self.client.post(delete_url)
        self.assertRedirects(r, article_url)

        # article contains comment
        r = self.client.get(article_url)
        self.assertNotContains(r, "Test Comment")


class ReplyToAuthor(AuthenticatedMemberMixin, TestCase):
    def test_reply_to_author(self):
        r = self.client.post(
            reverse("create-group-conversation", args=[self.group.pk]),
            {"subject": "Test", "text": "Test"},
            follow=True,
        )
        association = Association.objects.last()
        contribution = models.Contribution.objects.last()
        reply_url = reverse("reply-to-author", args=[association.pk, contribution.pk])

        # conversation page contains reply link
        self.assertContains(r, 'href="{}"'.format(reply_url))

        # member email contains reply link
        self.assertIn(reply_url, mail.outbox[0].body)

        # reply form renders without errors
        r = self.client.get(reply_url)
        self.assertEqual(r.status_code, 200)

        # posting reply generates new conversation
        r = self.client.post(reply_url, {"subject": "Reply", "text": "Test"})
        association = Conversation.objects.get(subject="Reply").associations.first()
        self.assertRedirects(r, reverse("conversation", args=[association.pk]))


class GuestCommentVisibilityOnPublicArticle(
    GroupArticleMixin, AuthenticatedMemberMixin, OtherGestaltMixin, Test
):

    ARTICLE_IS_PUBLIC_BY_DEFAULT = True
    COMMENT_SUBJECT_MAIL = "Comment from a non-member via email"
    COMMENT_SUBJECT_WEB = "Comment from a non-member via web"

    def _create_comment_by_other_via_email(self, message, **kwargs):
        EmailProcessor = ContributionMailProcessor()

        class CustomMessage:
            content = message
            date = timezone.now()
            attachments = []

        EmailProcessor._create_contribution(
            CustomMessage(), self.association.container, self.other_gestalt
        )

    def _create_comment_by_other_via_web(self, message, **kwargs):
        kwargs.update({"text": message, "public": False})
        response = self.client_other_gestalt.post(self.get_content_url(), kwargs)
        self.assertIn(response.status_code, {200, 302})

    def test_comment_via_mail_from_non_member_is_hidden_for_unauthenticated(self):
        """a comment from a non-member is private if submitted via email"""
        self._create_comment_by_other_via_email(self.COMMENT_SUBJECT_MAIL)
        article_url = reverse(
            "content", args=[self.association.entity.slug, self.association.slug]
        )
        r_member = self.client.get(article_url)
        self.assertContains(r_member, self.COMMENT_SUBJECT_MAIL)
        with self.temporary_client_login() as guest_client:
            r_guest = guest_client.get(article_url)
        self.assertNotContains(r_guest, self.COMMENT_SUBJECT_WEB)

    def test_comment_via_web_from_non_member_is_hidden_for_unauthenticated(self):
        """a comment from a non-member is public if submitted via the web interface"""
        self._create_comment_by_other_via_web(self.COMMENT_SUBJECT_WEB)
        article_url = reverse(
            "content", args=[self.association.entity.slug, self.association.slug]
        )
        r_member = self.client.get(article_url)
        self.assertContains(r_member, self.COMMENT_SUBJECT_WEB)
        with self.temporary_client_login() as guest_client:
            r_guest = guest_client.get(article_url)
        self.assertContains(r_guest, self.COMMENT_SUBJECT_WEB)
