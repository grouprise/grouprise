from content import models as content
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions
from utils import tests


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


class InternalGalleryInGroupWithOtherMember(
        subscriptions.NotificationToOtherGestalt,
        InternalGalleryMixin, memberships.OtherMemberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates an internal gallery
    * a notification to other members should be sent.
    """


class InternalGalleryInGroupWithOtherSubscriber(
        subscriptions.NoNotificationToOtherGestalt,
        InternalGalleryMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates an internal gallery
    * no notification to subscribers should be sent.
    """


class PublicGalleryInGroupWithOtherMember(
        subscriptions.NotificationToOtherGestalt,
        PublicGalleryMixin, memberships.OtherMemberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public gallery
    * a notification to other members should be sent.
    """


class PublicGalleryInGroupWithOtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        PublicGalleryMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates a public gallery
    * a notification to subscribers should be sent.
    """
