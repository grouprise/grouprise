from itertools import filterfalse

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase

from features.memberships.test_mixins import MemberMixin


class Subscription(MemberMixin, TestCase):
    TEST_EMAIL = 'test.subscription@test.local'

    def test_subscriptions(self):
        subscribe_url = reverse('group-subscribe', args=(self.group.pk,))

        # group page contains subscribe link
        r = self.client.get(self.group.get_absolute_url())
        self.assertContains(r, 'href="{}"'.format(subscribe_url))

        # subscribe form loads
        r = self.client.get(subscribe_url)
        self.assertEquals(r.status_code, 200)

        # subscription succeeds with email address
        r = self.client.post(subscribe_url, {'subscriber': self.TEST_EMAIL})
        self.assertRedirects(r, self.group.get_absolute_url())

        # subscriber gets notified on group content
        self.client.force_login(self.gestalt.user)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test', 'public': True})
        self.assertTrue(mail.outbox)
        self.assertTrue(list(filterfalse(
            lambda x: x < 0, map(lambda m: m.to[0].find(self.TEST_EMAIL), mail.outbox))))
