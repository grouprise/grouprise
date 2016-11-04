from content import models
import entities
from features.gestalten import tests as gestalten


class ContentMixin(gestalten.GestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        article = models.Article.objects.create(
                author=cls.gestalt, text='Test', title='Test', public=True)
        cls.content = models.Content.objects.get(article=article)


class NoAuthorContentMixin(
        gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin,
        ContentMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content.author = cls.other_gestalt
        cls.content.save()


class NoNotification:
    def test_content_creation(self):
        content = models.Article.objects.create(
                author=self.other_gestalt, title='Test Content')
        entities.models.GroupContent.objects.create(content=content, group=self.group)
        self.assertNoNotificationSent()
