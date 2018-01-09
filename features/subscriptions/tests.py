from itertools import filterfalse

from django.core import mail
from django.urls import reverse
from django.test import TestCase

from features.gestalten.tests import AuthenticatedMixin
from features.groups.tests.mixins import GroupMixin
from features.memberships.test_mixins import AuthenticatedMemberMixin, MemberMixin

TEST_EMAIL = 'test.subscription@test.local'


class Subscription(MemberMixin, TestCase):
    def test_subscriptions(self):
        subscribe_url = reverse('group-subscribe', args=(self.group.pk,))

        # group page contains subscribe link
        r = self.client.get(self.group.get_absolute_url())
        self.assertContains(r, 'href="{}"'.format(subscribe_url))

        # subscribe form loads
        r = self.client.get(subscribe_url)
        self.assertEquals(r.status_code, 200)

        # subscription succeeds with email address
        r = self.client.post(subscribe_url, {'subscriber': TEST_EMAIL})
        self.assertRedirects(r, self.group.get_absolute_url())

        # subscriber gets notified on group content
        self.client.force_login(self.gestalt.user)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test', 'public': True})
        self.assertTrue(mail.outbox)
        self.assertTrue(list(filterfalse(
            lambda x: x < 0, map(lambda m: m.to[0].find(TEST_EMAIL), mail.outbox))))


class AuthenticatedSubscription(AuthenticatedMixin, GroupMixin, TestCase):
    def test_authenticated_subscriptions(self):
        subscribe_url = reverse('group-subscribe', args=(self.group.pk,))
        unsubscribe_url = reverse('group-unsubscribe', args=(self.group.pk,))

        # group page contains subscribe form
        r = self.client.get(self.group.get_absolute_url())
        self.assertContains(r, 'action="{}"'.format(subscribe_url))

        # subscription succeeds
        r = self.client.post(subscribe_url)
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertTrue(self.gestalt in self.group.subscribers)

        # unsubscription succeeds
        r = self.client.post(unsubscribe_url)
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertFalse(self.gestalt in self.group.subscribers)


class MemberSubscription(AuthenticatedMemberMixin, TestCase):
    def test_member_subscription(self):
        unsubscribe_url = reverse('group-unsubscribe', args=(self.group.pk,))

        # subscribed member gets notified on internal content
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test', 'public': False})
        self.assertTrue(mail.outbox)
        self.assertTrue(list(filterfalse(
            lambda x: x < 0,
            map(lambda m: m.to[0].find(self.gestalt.user.email), mail.outbox))))

        # unsubscribed member does not get notified on internal content
        mail.outbox = []
        self.client.post(unsubscribe_url)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test', 'public': False})
        self.assertFalse(mail.outbox)
