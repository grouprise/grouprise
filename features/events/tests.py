from content import models as content
from core import tests
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class InternalEventMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Event.objects.create(
                author=cls.gestalt, time='2000-01-01 12:00+00:00')


class PublicEventMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Event.objects.create(
                author=cls.gestalt, public=True, time='2000-01-01 12:00+00:00',
                title='Test Event')


# class InternalEventInGroupWithOtherMember(
#         subscriptions.NotificationToOtherGestalt,
#         subscriptions.SenderNameIsGestalt,
#         InternalEventMixin, memberships.OtherMemberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal event
#     * a notification to other members should be sent.
#     * the sender name should be mentioned.
#     """


# class InternalEventInGroupWithOtherSubscriber(
#         subscriptions.NotificationToOtherGestalt,
#         InternalEventMixin, subscriptions.OtherGroupSubscriberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal event
#     * no notification to subscribers should be sent.
#     """


class PublicEventInGroupWithOtherMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        PublicEventMixin, memberships.OtherMemberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public event
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class PublicEventInGroupWithOtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderIsAnonymous,
        PublicEventMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public event
    * a notification to subscribers should be sent.
    * the sender name should not be mentioned.
    """
