import core.tests
from content import models as content
from core import tests
from features.associations import models as associations
from features.gestalten import tests as gestalten
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


class Guest(gestalten.GestaltMixin, core.tests.Test):
    def create_article(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Test', 'text': 'Test'})
        self.client.post(self.get_url('create-content'), kwargs)
        self.client.logout()

    def get_article_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def test_guest_article_link(self):
        self.assertNotContainsLink(self.client.get('/'), self.get_url('create-content'))
        self.assertNotContainsLink(
                self.client.get(self.get_url('articles')), self.get_url('create-content'))
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-content'))

    def test_guest_create_article(self):
        self.assertForbiddenOrLogin(
                self.client.get(self.get_url('create-content')),
                self.get_url('create-content'))
        self.assertForbiddenOrLogin(
                self.client.post(self.get_url('create-content')),
                self.get_url('create-content'))

    def test_guest_list_public_article(self):
        self.create_article(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())

    def test_guest_list_internal_article(self):
        self.create_article(public=False)
        self.assertNotContainsLink(self.client.get('/'), self.get_article_url())
        self.assertNotContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertNotContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())


class Gestalt(gestalten.AuthenticatedMixin, core.tests.Test):
    def create_article(self, **kwargs):
        kwargs.update({'title': 'Test', 'text': 'Test'})
        return self.client.post(self.get_url('create-content'), kwargs)

    def get_article_url(self):
        return associations.Association.objects.get(content__title='Test').get_absolute_url()

    def test_gestalt_article_link(self):
        self.assertContainsLink(self.client.get('/'), self.get_url('create-content'))
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_url('create-content'))
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_url('create-content'))

    def test_gestalt_create_article(self):
        self.assertEqual(self.client.get(self.get_url('create-content')).status_code, 200)
        response = self.create_article()
        self.assertRedirects(response, self.get_article_url())
        self.assertExists(associations.Association, content__title='Test')

    def test_gestalt_list_public_article(self):
        self.create_article(public=True)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())

    def test_gestalt_list_internal_article(self):
        self.create_article(public=False)
        self.assertContainsLink(self.client.get('/'), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.get_url('articles')), self.get_article_url())
        self.assertContainsLink(
                self.client.get(self.gestalt.get_absolute_url()), self.get_article_url())
