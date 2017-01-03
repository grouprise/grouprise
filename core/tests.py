"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

import django.core.urlresolvers
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

    def assertContainsLink(self, response=None, link_url=None, key=None, obj=None):
        if response is None:
            response = self.client.get(obj.get_absolute_url())
        self.assertContains(response, self.get_link(link_url, key))

    def assertNotContainsLink(self, response=None, link_url=None, key=None, obj=None):
        if response is None:
            response = self.client.get(obj.get_absolute_url())
        self.assertNotContains(response, self.get_link(link_url, key))

    def assertExists(self, model, **kwargs):
        qs = model.objects.filter(**kwargs)
        self.assertEqual(qs.count(), 1)
        return qs.first()

    def assertNotExists(self, model, **kwargs):
        self.assertFalse(model.objects.filter(**kwargs))

    def assertLogin(self, url=None, url_name=None, url_args=[], method='get'):
        if url is None:
            url = django.core.urlresolvers.reverse(url_name, args=url_args)
        response = getattr(self.client, method)(url)
        self.assertRedirects(response, self.get_login_url(url))

    def assertForbiddenOrLogin(self, response, next_url):
        if auth.get_user(self.client).is_authenticated():
            self.assertEqual(response.status_code, 403)
        else:
            self.assertRedirects(response, self.get_login_url(next_url))

    def assertOk(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def assertRedirect(self, url, method, data):
        response = getattr(self.client, method)(url, data)
        self.assertRedirects(response, url)

    def assertNotificationRecipient(self, gestalt):
        found = False
        for notification in mail.outbox:
            if notification.to[0].find(gestalt.user.email):
                found = True
        self.assertTrue(found)

    def assertNotificationSenderAnonymous(self):
        self.assertTrue(self.get_latest_notification().from_email.startswith(
            sites_models.Site.objects.get_current().name))

    def assertNotificationSenderName(self, gestalt):
        self.assertTrue(self.get_latest_notification().from_email.startswith(str(gestalt)))

    def assertNotificationHeaderContent(self, header, content):
        self.assertTrue(content in self.get_latest_notification().extra_headers[header])

    def assertNotificationContains(self, text):
        self.assertTrue(self.get_latest_notification().body.find(text) >= 0)

    def assertNoNotificationSent(self):
        self.assertEqual(len(mail.outbox), 0)

    def assertNotificationSent(self):
        self.assertTrue(len(mail.outbox) > 0)

    def assertNotificationsSent(self, num):
        self.assertEqual(len(mail.outbox), num)

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
        return 'href="{}"'.format(url)

    def get_login_url(self, next_url):
        return '{}?next={}'.format(
                urlresolvers.reverse('account_login'), next_url)

    def get_response(self, method, url):
        return getattr(self.client, method)(url)

    def get_latest_notification(self):
        return mail.outbox[-1]

    def get_url(self, url, key=None):
        if key is None:
            args = []
        elif isinstance(key, (list, tuple)):
            args = key
        else:
            args = [key]
        return urlresolvers.reverse(
                '{}'.format(url), args=args)

    def request(self, method, **kwargs):
        url = self.get_url(kwargs['url'], kwargs.get('key'))
        return self.get_response(method, url)
