from django import test
from django.contrib import auth
from django.contrib.sites import models as sites_models
from django.core import cache, mail, urlresolvers

HTTP_GET = 'get'
HTTP_POST = 'post'

HTTP_FORBIDDEN_OR_LOGIN = 'forbidden_or_login'
HTTP_REDIRECTS = 'redirects'
HTTP_OK = 'ok'


class Test(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.disable_caching()

    @classmethod
    def disable_caching(cls):
        cache.cache.cache = cache.caches['proxy']

    @classmethod
    def enable_caching(cls):
        cache.cache.cache = cache.caches['test']

    def assertContainsLink(self, response, url, key=None):
        self.assertContains(response, self.get_link(url, key))

    def assertNotContainsLink(self, response, url, key):
        self.assertNotContains(response, self.get_link(url, key))

    def assertExists(self, model, **kwargs):
        qs = model.objects.filter(**kwargs)
        self.assertEqual(qs.count(), 1)
        return qs.first()

    def assertNotExists(self, model, **kwargs):
        self.assertFalse(model.objects.filter(**kwargs))

    def assertForbiddenOrLogin(self, response, next_url):
        if auth.get_user(self.client).is_authenticated():
            self.assertEqual(response.status_code, 403)
        else:
            self.assertRedirects(response, self.get_login_url(next_url))

    def assertNotificationRecipient(self, gestalt):
        self.assertTrue(self.get_latest_notification().to[0].find(gestalt.user.email))

    def assertNotificationSenderAnonymous(self):
        self.assertTrue(self.get_latest_notification().from_email.startswith(
            sites_models.Site.objects.get_current().name))

    def assertNotificationSenderName(self, gestalt):
        self.assertTrue(self.get_latest_notification().from_email.startswith(str(gestalt)))

    def assertNotificationHeaderContent(self, header, content):
        self.assertTrue(content in self.get_latest_notification().extra_headers[header])

    def assertNoNotificationSent(self):
        self.assertEqual(len(mail.outbox), 0)

    def assertNotificationSent(self):
        self.assertEqual(len(mail.outbox), 1)

    def assertRequest(self, methods=[HTTP_GET], **kwargs):
        for method in methods:
            response = self.request(method, **kwargs)
            tests = kwargs['response']
            if HTTP_FORBIDDEN_OR_LOGIN in tests:
                self.assertForbiddenOrLogin(response, self.get_url(
                    kwargs['url'], kwargs.get('key')))
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

    def get_latest_notification(self):
        return mail.outbox[-1]

    def get_url(self, url, key=None):
        args = [key] if key else []
        return urlresolvers.reverse(
                '{}'.format(url), args=args)

    def request(self, method, **kwargs):
        url = self.get_url(kwargs['url'], kwargs.get('key'))
        return self.get_response(method, url)
