from django.contrib.contenttypes import models as contenttypes
from django.urls import reverse

import grouprise.core
import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from grouprise.core import tests
from grouprise.features.associations import models as associations
from grouprise.features.contributions import models as contributions
from grouprise.features.gestalten.tests.mixins import AuthenticatedMixin
from grouprise.features.groups.tests import mixins as groups
from grouprise.features.memberships import test_mixins as memberships

from . import models


def create_conversation(subject, content, sender, recipient_entity):
    conversation = models.Conversation.objects.create(subject=subject)
    conversation.contributions.create(
        author=sender,
        contribution=contributions.Text.objects.create(text=content),
    )
    association = associations.Association.objects.create(
        container=conversation, entity=recipient_entity
    )
    return association


class GestaltConversationMixin(
    grouprise.features.gestalten.tests.mixins.GestaltMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.association = create_conversation(
            "Test Thema", "Test Text", cls.gestalt, cls.other_gestalt
        )


class GroupConversationMixin(
    grouprise.features.gestalten.tests.mixins.GestaltMixin, groups.GroupMixin
):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.association = create_conversation(
            "Test Thema", "Test Text", cls.gestalt, cls.group
        )


class AuthenticatedGestaltConversationMixin(
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
):
    def _create_conversation_to_other(
        self, title: str = "Test Thema", body: str = "Test Text"
    ):
        with self.assertCreatedModelInstance(associations.Association) as new_objects:
            url = reverse("create-gestalt-conversation", args=[self.other_gestalt.pk])
            self.client.post(url, {"subject": title, "text": body})
        return new_objects[0]

    def setUp(self):
        super().setUp()
        self.association = self._create_conversation_to_other()


class AuthenticatedGroupConversationMixin(
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin, groups.GroupMixin
):
    def _create_conversation_to_group(
        self, title: str = "Test Thema", body: str = "Test Text"
    ):
        with self.assertCreatedModelInstance(associations.Association) as new_objects:
            url = reverse("create-group-conversation", args=[self.group.pk])
            self.client.post(url, {"subject": title, "text": body})
        return new_objects[0]

    def setUp(self):
        super().setUp()
        self.association = self._create_conversation_to_group()


class NotificationContainsConversationMessageIDs:
    def test_conversation_message_ids(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        self.client.post(conversation_url, {"text": "Test Reply"})
        self.assertNotificationSent()
        # example message ID: <conversation.18.text.33@example.com>
        self.assertNotificationHeaderContent(
            "Message-ID", "<conversation.%d." % self.association.pk
        )
        # the thread ID refers to the first message of this conversation
        # (the proper thread ID is hard to retrieve - we just verify its existence)
        self.assertNotificationHeaderContent(
            "References", "<conversation.%d." % self.association.pk
        )


class GroupPageHasCreateLink:
    def test_group_page_creation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(
            response, self.get_url("create-group-conversation", key=self.group.pk)
        )


class CanCreateGestaltConversationWithEmail:
    def test_create_gestalt_conversation_with_email(self):
        response = self.client.get(
            self.get_url("create-gestalt-conversation", key=self.other_gestalt.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.get_url("create-gestalt-conversation", key=self.other_gestalt.pk),
            tests.with_captcha(
                {
                    "author": "anonymous@example.org",
                    "subject": "Temp Test Thema",
                    "text": "Test Text",
                }
            ),
        )
        self.assertExists(
            associations.Association, conversation__subject="Temp Test Thema"
        )
        self.assertRedirects(response, self.other_gestalt.get_absolute_url())


class CanCreateGestaltConversation:
    def test_create_gestalt_conversation(self):
        response = self.client.get(
            self.get_url("create-gestalt-conversation", key=self.other_gestalt.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.get_url("create-gestalt-conversation", key=self.other_gestalt.pk),
            {
                "subject": "Temp Test Thema",
                "text": "Test Text",
            },
        )
        self.assertExists(
            associations.Association, conversation__subject="Temp Test Thema"
        )
        association = associations.Association.objects.get(
            conversation__subject="Temp Test Thema"
        )
        self.assertRedirects(response, self.get_url("conversation", key=association.pk))


class CanCreateGroupConversationWithEmail:
    def test_create_group_conversation_with_email(self):
        response = self.client.get(
            self.get_url("create-group-conversation", key=self.group.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.get_url("create-group-conversation", key=self.group.pk),
            tests.with_captcha(
                {
                    "author": "anonymous@example.org",
                    "subject": "Temp Test Thema",
                    "text": "Test Text",
                }
            ),
        )
        self.assertExists(
            associations.Association, conversation__subject="Temp Test Thema"
        )
        self.assertRedirects(response, self.group.get_absolute_url())


class CanCreateGroupConversation:
    def test_create_group_conversation(self):
        response = self.client.get(
            self.get_url("create-group-conversation", key=self.group.pk)
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            self.get_url("create-group-conversation", key=self.group.pk),
            {
                "subject": "Temp Test Thema",
                "text": "Test Text",
            },
        )
        self.assertExists(
            associations.Association, conversation__subject="Temp Test Thema"
        )
        association = associations.Association.objects.get(
            conversation__subject="Temp Test Thema"
        )
        self.assertRedirects(response, self.get_url("conversation", key=association.pk))


class GroupPageHasConversationLink:
    def test_group_page_conversation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(
            response, self.get_url("conversation", key=self.association.pk)
        )


class GroupPageDoesNotHaveConversationLink:
    def test_group_page_not_conversation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(
            response, self.get_url("conversation", key=self.association.pk)
        )


class CanViewGestaltConversation:
    def test_view_gestalt_conversation(self):
        response = self.client.get(
            self.get_url("conversation", key=self.association.pk)
        )
        self.assertEquals(response.status_code, 200)


class CanNotViewGestaltConversation:
    def test_not_view_gestalt_conversation(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class CanViewGroupConversation:
    def test_view_group_conversation(self):
        response = self.client.get(
            self.get_url("conversation", key=self.association.pk)
        )
        self.assertEquals(response.status_code, 200)


class CanNotViewGroupConversation:
    def test_not_view_group_conversation(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class OtherGestaltCanNotViewGroupConversation:
    def test_view_conversation_as_other(self):
        self.client.logout()
        self.client.force_login(self.other_gestalt.user)
        conversation_url = self.get_url("conversation", key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class CanReplyToConversation:
    def test_reply_to_conversation(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        response = self.client.post(
            conversation_url,
            {
                "text": "Test Reply",
            },
        )
        self.assertRedirects(response, conversation_url)
        t = self.assertExists(contributions.Text, text="Test Reply")
        self.assertExists(
            models.Conversation,
            contributions__contribution_id=t.id,
            contributions__contribution_type=contenttypes.ContentType.objects.get_for_model(
                t
            ),
        )


class OtherGestaltIsNotifiedOnGestaltConversation:
    def test_gestalt_is_notified_on_gestalt_conversation(self):
        self.client.post(
            self.get_url("create-gestalt-conversation", key=self.other_gestalt.pk),
            {
                "subject": "Temp Test Thema",
                "text": "Test Text",
            },
        )
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationSenderName(self.gestalt)


class OtherGestaltIsNotifiedOnReply:
    def test_is_notified_on_reply(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        self.client.post(
            conversation_url,
            {
                "text": "Test Reply",
            },
        )
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationSenderName(self.gestalt)


class CanNotReplyToConversation:
    def test_cannot_reply_to_conversation(self):
        conversation_url = self.get_url("conversation", key=self.association.pk)
        response = self.client.post(
            conversation_url,
            {
                "text": "Test Reply",
            },
        )
        self.assertForbiddenOrLogin(response, conversation_url)


class Anonymous(
    GroupPageHasCreateLink,
    CanCreateGroupConversationWithEmail,
    GroupPageDoesNotHaveConversationLink,
    CanNotViewGroupConversation,
    CanNotReplyToConversation,
    CanCreateGestaltConversationWithEmail,
    CanNotViewGestaltConversation,
    GestaltConversationMixin,
    GroupConversationMixin,
    tests.Test,
):
    """
    An anonymous visitor
    * should see a message creation link on the group page
    """

    def setUp(self):
        self.other_gestalt.public = True
        self.other_gestalt.save()


class AuthenticatedGroupConversationTestCase(
    GroupPageHasCreateLink,
    CanCreateGroupConversation,
    GroupPageHasConversationLink,
    CanViewGroupConversation,
    CanReplyToConversation,
    GroupConversationMixin,
    AuthenticatedMixin,
    tests.Test,
):
    """
    An authenticated visitor
    """


class AuthenticatedGestaltConversationTestCase(
    CanCreateGestaltConversation,
    CanViewGestaltConversation,
    CanReplyToConversation,
    GestaltConversationMixin,
    AuthenticatedMixin,
    tests.Test,
):
    """
    An authenticated visitor
    """


class GroupMember(
    GroupPageHasCreateLink,
    CanCreateGroupConversation,
    GroupPageHasConversationLink,
    CanViewGroupConversation,
    OtherGestaltCanNotViewGroupConversation,
    CanReplyToConversation,
    GroupConversationMixin,
    memberships.AuthenticatedMemberMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
    tests.Test,
):
    """
    A group member
    * should see a message creation link on the group page
    """


class TwoGroupMembers(
    OtherGestaltIsNotifiedOnReply,
    OtherGestaltIsNotifiedOnGestaltConversation,
    NotificationContainsConversationMessageIDs,
    GroupConversationMixin,
    memberships.OtherAuthenticatedMemberMixin,
    memberships.AuthenticatedMemberMixin,
    tests.Test,
):
    """ """


class TestUrls(grouprise.core.tests.Test):
    def test_404(self):
        r = self.client.get(self.get_url("conversation", 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url("create-gestalt-conversation", 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url("group-conversations", 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url("create-group-conversation", 0))
        self.assertEqual(r.status_code, 404)
