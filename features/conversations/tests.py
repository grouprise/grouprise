from content import models as content
from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class MessageMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.gestalt, public=False, title='Test Message')


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
