from content import models as content
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions
from utils import tests


class ArticleMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.gestalt, public=True, title='Test Article')


class OtherMember(
        subscriptions.NotificationToOtherGestalt,
        ArticleMixin, memberships.OtherMemberMixin, memberships.MemberMixin,
        tests.Test):
    """
    If a group member creates an article
    * a notification to other members should be sent.
    """


class OtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        ArticleMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates an article
    * a notification to subscribers should be sent.
    """
