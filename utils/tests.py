from content import models as content_models
from django import test
from django.contrib import auth
from django.core import mail, urlresolvers
from entities import models as entities_models
from features.memberships import models as memberships_models

HTTP_GET = 'get'
HTTP_POST = 'post'

HTTP_FORBIDDEN_OR_LOGIN = 'forbidden_or_login'
HTTP_REDIRECTS = 'redirects'
HTTP_OK = 'ok'


class GestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.gestalt = auth.get_user_model().objects.create(
                email='test@example.org', username='test').gestalt


class OtherGestaltMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.other_gestalt = auth.get_user_model().objects.create(
                email='test2@example.org', username='test2').gestalt


class AuthenticatedMixin(GestaltMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(
                self.gestalt.user, 'django.contrib.auth.backends.ModelBackend')


class ContentMixin(GestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        article = content_models.Article.objects.create(
                author=cls.gestalt, text='Test', title='Test', public=True)
        cls.content = content_models.Content.objects.get(article=article)


class GroupMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = entities_models.Group.objects.create(name='Test')


class ClosedGroupMixin(GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group.closed = True
        cls.group.save()


class NoAuthorContentMixin(AuthenticatedMixin, ContentMixin, OtherGestaltMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content.author = cls.other_gestalt
        cls.content.save()


class Test(test.TestCase):
    def assertContainsLink(self, response, url, key):
        self.assertContains(response, self.get_link(url, key))

    def assertNotContainsLink(self, response, url, key):
        self.assertNotContains(response, self.get_link(url, key))

    def assertExists(self, model, **kwargs):
        self.assertTrue(model.objects.filter(**kwargs))

    def assertNotExists(self, model, **kwargs):
        self.assertFalse(model.objects.filter(**kwargs))

    def assertForbiddenOrLogin(self, response, next_url):
        if auth.get_user(self.client).is_authenticated():
            self.assertEqual(response.status_code, 403)
        else:
            self.assertRedirects(response, self.get_login_url(next_url))

    def assertNotificationRecipient(self, gestalt):
        self.assertTrue(mail.outbox[0].to[0].find(gestalt.user.email))

    def assertNoNotificationSent(self):
        self.assertEqual(len(mail.outbox), 0)

    def assertNotificationSent(self):
        self.assertEqual(len(mail.outbox), 1)

    def assertRequest(self, **kwargs):
        for method in kwargs['methods']:
            response = self.request(method, **kwargs)
            tests = kwargs['response']
            if HTTP_FORBIDDEN_OR_LOGIN in tests:
                self.assertForbiddenOrLogin(response, self.get_url(kwargs['url'], kwargs['key']))
            if HTTP_REDIRECTS in tests:
                url = tests[HTTP_REDIRECTS]
                if isinstance(url, tuple):
                    url = self.get_url(*url)
                self.assertRedirects(response, url)
            if HTTP_OK in tests:
                self.assertEqual(response.status_code, 200)

    def get_link(self, url, key):
        return 'href="{}"'.format(self.get_url(url, key))

    def get_login_url(self, next_url):
        return '{}?next={}'.format(
                urlresolvers.reverse('account_login'), next_url)

    def get_response(self, method, url):
        return getattr(self.client, method)(url)

    def get_url(self, url, key=None):
        args = [key] if key else []
        return urlresolvers.reverse(
                '{}'.format(url), args=args)

    def request(self, method, **kwargs):
        url = self.get_url(kwargs['url'], kwargs['key'])
        return self.get_response(method, url)
