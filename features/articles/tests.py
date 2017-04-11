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


class Guest(core.tests.Test):
    def test_guest_article_link(self):
        self.assertNotContainsLink(self.client.get('/'), 'create-content')

    def test_guest_create_article(self):
        self.assertForbiddenOrLogin(
                self.client.get(self.get_url('create-content')),
                self.get_url('create-content'))
        self.assertForbiddenOrLogin(
                self.client.post(self.get_url('create-content')),
                self.get_url('create-content'))


class Gestalt(gestalten.AuthenticatedMixin, core.tests.Test):
    def test_gestalt_article_link(self):
        self.assertContainsLink(self.client.get('/'), 'create-content')

    def test_gestalt_create_article(self):
        self.assertEqual(self.client.get(self.get_url('create-content')).status_code, 200)
        self.assertRedirects(self.client.post(self.get_url('create-content'), {
            'title': 'Test', 'text': 'Test'}), '/test/test/')
        self.assertExists(associations.Association, content__title='Test')
