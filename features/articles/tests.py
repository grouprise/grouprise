from content import models as content
from entities import models as entities
from features.memberships import test_mixins as memberships
from utils import tests


class ArticleMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Article.objects.create(author=cls.gestalt)


class NotificationToOtherGestalt:
    def test_associate_content(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class Article(
        NotificationToOtherGestalt,
        ArticleMixin, memberships.TwoMembersMixin, tests.Test):
    """
    If a group member creates an article
    * a notification should be sent.
    """
