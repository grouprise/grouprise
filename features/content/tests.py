from content import models
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
