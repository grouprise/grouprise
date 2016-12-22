from content import models as content
from core import tests
from django import test
from django.core import urlresolvers
import entities.models
from features.associations import models as associations
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships
# from features.subscriptions import test_mixins as subscriptions


class ConversationMixin(memberships.MemberMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.gestalt, public=False, title='Test Message')
        entities.models.GroupContent.objects.create(content=cls.content, group=cls.group)


class ExternalConversationMixin(memberships.MemberMixin, gestalten.OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.other_gestalt, public=False, title='Test Message')
        entities.models.GroupContent.objects.create(content=cls.content, group=cls.group)


class MessageMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.gestalt, public=False, title='Test Message')


class NoNotificationOnExternalConversation:
    def test_external_conversation(self):
        conversation = content.Article.objects.create(
                author=self.other_gestalt, public=False, title='Test Message')
        entities.models.GroupContent.objects.create(content=conversation, group=self.group)
        self.assertNoNotificationSent()


class GroupPageHasCreateLink(groups.GroupMixin):
    def test_group_page(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, 'message-create', key=self.group.pk)


class CanCreateConversationWithEmail(groups.GroupMixin):
    def test_create_conversation(self):
        response = self.client.get(self.get_url('message-create', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('message-create', key=self.group.pk),
                {
                    'author': 'anonymous@example.org',
                    'subject': 'Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Test Thema')
        self.assertRedirects(response, self.group.get_absolute_url())


class CanCreateConversation(groups.GroupMixin):
    def test_create_conversation(self):
        response = self.client.get(self.get_url('message-create', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('message-create', key=self.group.pk),
                {
                    'subject': 'Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Test Thema')
        association = associations.Association.objects.first()
        self.assertRedirects(response, self.get_url('conversation', key=association.pk))


class Anonymous(
        GroupPageHasCreateLink,
        CanCreateConversationWithEmail,
        tests.Test):
    '''
    An anonymous visitor
    * should see a message creation link on the group page
    '''


class Authenticated(
        GroupPageHasCreateLink,
        CanCreateConversation,
        gestalten.AuthenticatedMixin, tests.Test):
    '''
    An authenticated visitor
    * should see a message creation link on the group page
    '''


class GroupMember(
        GroupPageHasCreateLink,
        CanCreateConversation,
        memberships.MemberMixin, tests.Test):
    '''
    A group member
    * should see a message creation link on the group page
    '''


# class NoMemberAndMember(
#         subscriptions.NotificationToOtherGestalt,
#         subscriptions.SenderNameIsGestalt,
#         MessageMixin, memberships.OtherMemberMixin, gestalten.GestaltMixin,
#         groups.GroupMixin, tests.Test):
#     """
#     If a group member creates a message
#     * a notification to other members should be sent.
#     * the sender name should be mentioned.
#     """


# class MemberAndOtherMember(
#         subscriptions.NotificationToOtherGestalt,
#         subscriptions.SenderNameIsGestalt,
#         MessageMixin, memberships.OtherMemberMixin, memberships.MemberMixin,
#         tests.Test):
#     """
#     If a group member creates a message
#     * a notification to other members should be sent.
#     * the sender name should be mentioned.
#     """


# class MemberAndSubscriber(
#         subscriptions.NoNotificationToOtherGestalt,
#         MessageMixin, subscriptions.OtherGroupSubscriberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates a message
#     * no notification to subscribers should be sent.
#     """
