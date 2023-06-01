import contextlib
import logging

import django.urls
from django import test, urls
from django.contrib import auth
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from huey.contrib.djhuey import task

from .matrix import MatrixConsoleClient
from .settings import get_grouprise_site
from .utils import hash_captcha_answer

HTTP_GET = "get"
HTTP_POST = "post"

HTTP_FORBIDDEN_OR_LOGIN = "forbidden_or_login"
HTTP_REDIRECTS = "redirects"
HTTP_OK = "ok"


def get_url(url, *args):
    return django.urls.reverse(url, args=args)


def with_captcha(data, answer="foo", field_name="captcha"):
    data.update(
        {field_name + "_0": answer, field_name + "_1": hash_captcha_answer(answer)}
    )
    return data


@task(name="grouprise-core-test-huey-immediate-mode")
def _dummy_task_append_to_list(input_data: list) -> None:
    input_data.append(True)


class Test(test.TestCase):
    def assertContainsLink(self, response=None, link_url=None, key=None, obj=None):
        if response is None:
            response = self.client.get(obj.get_absolute_url())
        self.assertContains(response, self.get_link(link_url, key))

    def assertNotContainsLink(self, response=None, link_url=None, key=None, obj=None):
        if response is None:
            response = self.client.get(obj.get_absolute_url())
        self.assertNotContains(response, self.get_link(link_url, key))

    @contextlib.contextmanager
    def assertCreatedModelInstance(self, model: models.Model, expected_count=1):
        """track model instances created during the life time of the context

        The yielded value is a list, which is supposed to be evaluated *after* the context is
        finished.
        This list contains the recently created instances.
        """
        new_items = []
        before_pks = set(model.objects.values_list("pk", flat=True))
        yield new_items
        after_pks = set(model.objects.values_list("pk", flat=True))
        new_items.extend(
            [model.objects.get(pk=pk) for pk in sorted(after_pks - before_pks)]
        )
        self.assertEqual(len(new_items), expected_count)

    def assertExists(self, model, **kwargs):
        qs = model.objects.filter(**kwargs)
        self.assertEqual(qs.count(), 1)
        return qs.first()

    def assertNotExists(self, model, **kwargs):
        self.assertFalse(model.objects.filter(**kwargs))

    def assertForbidden(self, url=None, method="get"):
        response = getattr(self.client, method)(url)
        self.assertEqual(response.status_code, 403)

    def assertLogin(self, url=None, url_name=None, url_args=[], method="get"):
        if url is None:
            url = django.urls.reverse(url_name, args=url_args)
        response = getattr(self.client, method)(url)
        self.assertRedirects(response, self.get_login_url(url))

    def assertForbiddenOrLogin(self, response, next_url):
        if auth.get_user(self.client).is_authenticated:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertRedirects(response, self.get_login_url(next_url))

    def assertOk(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def assertRedirect(self, url, method, data, other=None):
        response = getattr(self.client, method)(url, data)
        self.assertRedirects(response, other or url)

    def _count_notifications_for_recipient(self, gestalt):
        count = 0
        for notification in mail.outbox:
            if gestalt.user.email in notification.to[0]:
                count += 1
        return count

    def assertNotificationRecipient(self, gestalt):
        self.assertGreater(self._count_notifications_for_recipient(gestalt), 0)

    def assertNotNotificationRecipient(self, gestalt):
        self.assertEqual(self._count_notifications_for_recipient(gestalt), 0)

    def assertNotificationSenderAnonymous(self):
        self.assertTrue(
            self.get_latest_notification().from_email.startswith(
                get_grouprise_site().name
            )
        )

    def assertNotificationSenderName(self, gestalt):
        self.assertTrue(
            self.get_latest_notification().from_email.startswith(str(gestalt))
        )

    def assertNotificationHeaderContent(self, header, content):
        self.assertIn(content, self.get_latest_notification().extra_headers[header])

    def assertNotificationContains(self, text):
        self.assertIn(text, self.get_latest_notification().body)

    def assertNoNotificationSent(self):
        self.assertEqual(len(mail.outbox), 0)

    def assertNotificationSent(self):
        self.assertGreater(len(mail.outbox), 0)

    def assertNotificationsSent(self, num):
        self.assertEqual(len(mail.outbox), num)

    def assertRequest(self, methods=[HTTP_GET], **kwargs):
        for method in methods:
            response = self.request(method, **kwargs)
            tests = kwargs["response"]
            if HTTP_FORBIDDEN_OR_LOGIN in tests:
                self.assertForbiddenOrLogin(
                    response, self.get_url(kwargs["url"], kwargs.get("key"))
                )
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
        return "{}?next={}".format(urls.reverse("account_login"), next_url)

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
        return urls.reverse("{}".format(url), args=args)

    def request(self, method, **kwargs):
        url = self.get_url(kwargs["url"], kwargs.get("key"))
        return self.get_response(method, url)

    @classmethod
    def _verify_task_runner_immediate_mode(cls):
        task_was_executed = []

        # Run the task: this will happen in the background (later), if huey is not configured for
        # "immediate" execution.
        _dummy_task_append_to_list(task_was_executed)
        if not task_was_executed:
            raise ImproperlyConfigured(
                "For unknown reasons, 'huey' is not configured in 'immediate' mode."
                " Maybe the default settings were changed locally?",
            )

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)
        MatrixConsoleClient.output_stream = None
        cls._verify_task_runner_immediate_mode()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)
