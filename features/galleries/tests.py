from content import models as content
from core import tests
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class InternalGalleryMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Gallery.objects.create(author=cls.gestalt)


class PublicGalleryMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Gallery.objects.create(
                author=cls.gestalt, public=True, title='Test Event')


# class InternalGalleryInGroupWithOtherMember(
#         subscriptions.NotificationToOtherGestalt,
#         subscriptions.SenderNameIsGestalt,
#         InternalGalleryMixin, memberships.OtherMemberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal gallery
#     * a notification to other members should be sent.
#     * the sender name should be mentioned.
#     """


# class InternalGalleryInGroupWithOtherSubscriber(
#         subscriptions.NoNotificationToOtherGestalt,
#         InternalGalleryMixin, subscriptions.OtherGroupSubscriberMixin,
#         memberships.MemberMixin, tests.Test):
#     """
#     If a group member creates an internal gallery
#     * no notification to subscribers should be sent.
#     """


class PublicGalleryInGroupWithOtherMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        PublicGalleryMixin, memberships.OtherMemberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public gallery
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class PublicGalleryInGroupWithOtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderIsAnonymous,
        PublicGalleryMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public gallery
    * a notification to subscribers should be sent.
    * the sender name should not be mentioned.
    """
