from content import models as content
from core import tests
from features.memberships import test_mixins as memberships
from features.subscriptions import test_mixins as subscriptions


class ArticleMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(
                author=cls.gestalt, public=True, title='Test Article')


class OtherMember(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderNameIsGestalt,
        ArticleMixin, memberships.OtherMemberMixin, memberships.MemberMixin,
        tests.Test):
    """
    If a group member creates an article
    * a notification to other members should be sent.
    * the sender name should be mentioned.
    """


class OtherSubscriber(
        subscriptions.NotificationToOtherGestalt,
        subscriptions.SenderIsAnonymous,
        ArticleMixin, subscriptions.OtherGroupSubscriberMixin,
        memberships.MemberMixin, tests.Test):
    """
    If a group member creates an article
    * a notification to subscribers should be sent.
    * the sender name should not be mentioned.
    """
