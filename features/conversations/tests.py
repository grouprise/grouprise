from content import models as content
from core import tests
import entities.models
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


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


class NoMemberAndMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        MessageMixin, memberships.OtherMemberMixin, gestalten.GestaltMixin,
        groups.GroupMixin, tests.Test):
    """
    If a group member creates a message
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class MemberAndOtherMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        MessageMixin, memberships.OtherMemberMixin, memberships.MemberMixin,
        tests.Test):
    """
    If a group member creates a message
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class MemberAndSubscriber(
        subscriptions.NoNotificationToOtherGestalt,
        MessageMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a message
    * no notification to subscribers should be sent.
    """
