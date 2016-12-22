from . import models
from content import models as content
from core import tests
import entities.models
from features.associations import models as associations
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships
# from features.subscriptions import test_mixins as subscriptions


class Conversation(gestalten.GestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        conversation = models.Conversation.objects.create(subject='Test Thema')
        conversation.texts.create(author=cls.gestalt, text='Test Text')
        cls.association = associations.Association.objects.create(
                container=conversation, entity=cls.group)


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


class GroupPageHasCreateLink:
    def test_group_page_creation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, 'message-create', key=self.group.pk)


class CanCreateConversationWithEmail:
    def test_create_conversation(self):
        response = self.client.get(self.get_url('message-create', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('message-create', key=self.group.pk),
                {
                    'author': 'anonymous@example.org',
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Temp Test Thema')
        self.assertRedirects(response, self.group.get_absolute_url())


class CanCreateConversation:
    def test_create_conversation(self):
        response = self.client.get(self.get_url('message-create', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('message-create', key=self.group.pk),
                {
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Temp Test Thema')
        association = associations.Association.objects.get(
                conversation__subject='Temp Test Thema')
        self.assertRedirects(response, self.get_url('conversation', key=association.pk))


class GroupPageHasConversationLink:
    def test_group_page_conversation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, 'conversation', key=self.association.pk)


class GroupPageDoesNotHaveConversationLink:
    def test_group_page_conversation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, 'conversation', key=self.association.pk)


class Anonymous(
        GroupPageHasCreateLink,
        CanCreateConversationWithEmail,
        GroupPageDoesNotHaveConversationLink,
        Conversation, tests.Test):
    '''
    An anonymous visitor
    * should see a message creation link on the group page
    '''


class Authenticated(
        GroupPageHasCreateLink,
        CanCreateConversation,
        GroupPageHasConversationLink,
        Conversation, gestalten.AuthenticatedMixin, tests.Test):
    '''
    An authenticated visitor
    * should see a message creation link on the group page
    '''


class GroupMember(
        GroupPageHasCreateLink,
        CanCreateConversation,
        GroupPageHasConversationLink,
        Conversation, memberships.MemberMixin, tests.Test):
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
