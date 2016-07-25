from django import test
from django.contrib import auth
from django.core import urlresolvers
from entities import models as entities_models
from features.memberships import models as memberships_models

HTTP_GET = 'get'
HTTP_POST = 'post'

HTTP_FORBIDDEN_OR_LOGIN = 'forbidden_or_login'
HTTP_REDIRECTS = 'redirects'
HTTP_OK = 'ok'


class AuthenticatedMixin:
    def setUp(self):
        super().setUp()
        self.client.force_login(self.gestalt.user)


class GroupMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = entities_models.Group.objects.create(name='Test')


class MemberMixin(AuthenticatedMixin, GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        memberships_models.Membership.objects.create(
                group=cls.group, member=cls.gestalt)


class Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gestalt = auth.get_user_model().objects.create(
                email='test@example.org').gestalt

    def setUp(self):
        self.client = test.Client()

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

    def assertRequest(self, **kwargs):
        for method in kwargs['methods']:
            response = self.request(method, **kwargs)
            tests = kwargs['response']
            if HTTP_FORBIDDEN_OR_LOGIN in tests:
                self.assertForbiddenOrLogin(response, self.get_url(kwargs['url'], kwargs['key']))
            if HTTP_REDIRECTS in tests:
                data = tests[HTTP_REDIRECTS]
                self.assertRedirects(response, self.get_url(*data))
            if HTTP_OK in tests:
                self.assertEqual(response.status_code, 200)

    def get_link(self, url, key):
        return 'href="{}"'.format(self.get_url(url, key))

    def get_login_url(self, next_url):
        return '{}?next={}'.format(
                urlresolvers.reverse('account_login'), next_url)

    def get_response(self, method, url):
        return getattr(self.client, method)(url)

    def get_url(self, url, key):
        return urlresolvers.reverse(
                '{}'.format(url), args=[key])

    def request(self, method, **kwargs):
        url = self.get_url(kwargs['url'], kwargs['key'])
        return self.get_response(method, url)
