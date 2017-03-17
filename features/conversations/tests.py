from . import models
from content import models as content
from core import tests
from django.contrib.contenttypes import models as contenttypes
import entities.models
from features.associations import models as associations
from features.contributions import models as contributions
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class GestaltConversation(gestalten.GestaltMixin, gestalten.OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        conversation = models.Conversation.objects.create(subject='Test Thema')
        conversation.contributions.create(
                author=cls.gestalt, contribution=contributions.Text.objects.create(
                    text='Test Text'))
        cls.association = associations.Association.objects.create(
                container=conversation, entity=cls.group)


class GroupConversation(gestalten.GestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        conversation = models.Conversation.objects.create(subject='Test Thema')
        conversation.contributions.create(
                author=cls.gestalt, contribution=contributions.Text.objects.create(
                    text='Test Text'))
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


class NotificationContainsConversationMessageIDs:
    def test_conversation_message_ids(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        self.client.post(conversation_url, {'text': 'Test Reply'})
        self.assertNotificationSent()
        # example message ID: <conversation.18.text.33@example.com>
        self.assertNotificationHeaderContent('Message-ID',
                                             '<conversation.%d.' % self.association.pk)
        # the thread ID refers to the first message of this conversation
        # (the proper tread ID is hard to retrieve - we just verify its existence)
        self.assertNotificationHeaderContent('References',
                                             '<conversation.%d.' % self.association.pk)


class GroupPageHasCreateLink:
    def test_group_page_creation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, 'create-group-conversation', key=self.group.pk)


class CanCreateGestaltConversationWithEmail:
    def test_create_gestalt_conversation_with_email(self):
        response = self.client.get(
                self.get_url('create-gestalt-conversation', key=self.other_gestalt.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('create-gestalt-conversation', key=self.other_gestalt.pk),
                {
                    'author': 'anonymous@example.org',
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Temp Test Thema')
        self.assertRedirects(response, self.other_gestalt.get_absolute_url())


class CanCreateGestaltConversation:
    def test_create_gestalt_conversation(self):
        response = self.client.get(
                self.get_url('create-gestalt-conversation', key=self.other_gestalt.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('create-gestalt-conversation', key=self.other_gestalt.pk),
                {
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Temp Test Thema')
        association = associations.Association.objects.get(
                conversation__subject='Temp Test Thema')
        self.assertRedirects(response, self.get_url('conversation', key=association.pk))


class CanCreateGroupConversationWithEmail:
    def test_create_group_conversation_with_email(self):
        response = self.client.get(self.get_url('create-group-conversation', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('create-group-conversation', key=self.group.pk),
                {
                    'author': 'anonymous@example.org',
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertExists(associations.Association, conversation__subject='Temp Test Thema')
        self.assertRedirects(response, self.group.get_absolute_url())


class CanCreateGroupConversation:
    def test_create_group_conversation(self):
        response = self.client.get(self.get_url('create-group-conversation', key=self.group.pk))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
                self.get_url('create-group-conversation', key=self.group.pk),
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
    def test_group_page_not_conversation(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, 'conversation', key=self.association.pk)


class CanViewGestaltConversation:
    def test_view_gestalt_conversation(self):
        response = self.client.get(self.get_url('conversation', key=self.association.pk))
        self.assertEquals(response.status_code, 200)


class CanNotViewGestaltConversation:
    def test_not_view_gestalt_conversation(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class CanViewGroupConversation:
    def test_view_group_conversation(self):
        response = self.client.get(self.get_url('conversation', key=self.association.pk))
        self.assertEquals(response.status_code, 200)


class CanNotViewGroupConversation:
    def test_not_view_group_conversation(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class OtherGestaltCanNotViewGroupConversation:
    def test_view_conversation_as_other(self):
        self.client.logout()
        self.client.force_login(self.other_gestalt.user)
        conversation_url = self.get_url('conversation', key=self.association.pk)
        response = self.client.get(conversation_url)
        self.assertForbiddenOrLogin(response, conversation_url)


class CanReplyToConversation:
    def test_reply_to_conversation(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        response = self.client.post(
                conversation_url,
                {
                    'text': 'Test Reply',
                })
        self.assertRedirects(response, conversation_url)
        t = self.assertExists(contributions.Text, text='Test Reply')
        self.assertExists(
                models.Conversation,
                contributions__contribution_id=t.id,
                contributions__contribution_type=contenttypes.ContentType.objects.get_for_model(
                    t))


class OtherGestaltIsNotifiedOnGestaltConversation:
    def test_gestalt_is_notified_on_gestalt_conversation(self):
        self.client.post(
                self.get_url('create-gestalt-conversation', key=self.other_gestalt.pk),
                {
                    'subject': 'Temp Test Thema',
                    'text': 'Test Text',
                })
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationSenderName(self.gestalt)


class OtherGestaltIsNotifiedOnReply:
    def test_is_notified_on_reply(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        self.client.post(
                conversation_url,
                {
                    'text': 'Test Reply',
                })
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)
        self.assertNotificationSenderName(self.gestalt)


class CanNotReplyToConversation:
    def test_cannot_reply_to_conversation(self):
        conversation_url = self.get_url('conversation', key=self.association.pk)
        response = self.client.post(
                conversation_url,
                {
                    'text': 'Test Reply',
                })
        self.assertForbiddenOrLogin(response, conversation_url)


class Anonymous(
        GroupPageHasCreateLink,
        CanCreateGroupConversationWithEmail,
        GroupPageDoesNotHaveConversationLink,
        CanNotViewGroupConversation,
        CanNotReplyToConversation,

        CanCreateGestaltConversationWithEmail,
        CanNotViewGestaltConversation,

        GestaltConversation, GroupConversation, tests.Test):
    '''
    An anonymous visitor
    * should see a message creation link on the group page
    '''


class Authenticated(
        GroupPageHasCreateLink,
        CanCreateGroupConversation,
        GroupPageHasConversationLink,
        CanViewGroupConversation,
        CanReplyToConversation,

        CanCreateGestaltConversation,
        CanViewGestaltConversation,

        GestaltConversation, GroupConversation, gestalten.AuthenticatedMixin, tests.Test):
    '''
    An authenticated visitor
    * should see a message creation link on the group page
    '''


class GroupMember(
        GroupPageHasCreateLink,
        CanCreateGroupConversation,
        GroupPageHasConversationLink,
        CanViewGroupConversation,
        OtherGestaltCanNotViewGroupConversation,
        CanReplyToConversation,

        GroupConversation, memberships.MemberMixin, gestalten.OtherGestaltMixin, tests.Test):
    '''
    A group member
    * should see a message creation link on the group page
    '''


class TwoGroupMembers(
        OtherGestaltIsNotifiedOnReply,
        OtherGestaltIsNotifiedOnGestaltConversation,
        NotificationContainsConversationMessageIDs,

        GroupConversation, memberships.OtherMemberMixin, memberships.MemberMixin, tests.Test):
    '''
    '''
