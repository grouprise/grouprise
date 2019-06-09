from itertools import filterfalse

from django.core import mail
from django.urls import reverse
from django.test import TestCase

from grouprise.core.models import PermissionToken
from grouprise.features.gestalten.tests import AuthenticatedMixin
from grouprise.features.groups.tests.mixins import GroupMixin
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin, MemberMixin
from . import models

TEST_EMAIL = 'test.subscription@test.local'


class Subscription(MemberMixin, TestCase):
    def test_subscriptions(self):
        subscribe_url = reverse('group-subscribe', args=(self.group.slug,))

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
        for email_obj in mail.outbox:
            if email_obj.to[0].find(TEST_EMAIL) >= 0:
                break
        self.assertIn(TEST_EMAIL, email_obj.to[0])

        # cleanup
        mail.outbox = []
        self.client.logout()

        # notification contains link to unsubscribe form
        unsubscribe_request_url = reverse('group-unsubscribe-request', args=(self.group.pk,))
        self.assertTrue(unsubscribe_request_url in email_obj.body)

        # unsubscribe form renders ok
        r = self.client.get(unsubscribe_request_url)
        self.assertEquals(r.status_code, 200)

        # unsubscription succeeds with email address
        r = self.client.post(unsubscribe_request_url, {'subscriber': TEST_EMAIL})
        self.assertRedirects(r, self.group.get_absolute_url())

        # subscriber gets email with link to unsubscribe confirmation
        token = PermissionToken.objects.get(feature_key='group-unsubscribe')
        unsubscribe_confirm_url = reverse('group-unsubscribe-confirm', args=(token.secret_key,))
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(unsubscribe_confirm_url in mail.outbox[0].body)

        # unsubscription confirmation page renders ok
        r = self.client.get(unsubscribe_confirm_url)
        self.assertEquals(r.status_code, 200)

        # unsubscription confirmation removes subscription
        num_subscriptions = models.Subscription.objects.count()
        r = self.client.post(unsubscribe_confirm_url)
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertEqual(models.Subscription.objects.count(), num_subscriptions-1)


class AuthenticatedSubscription(AuthenticatedMixin, GroupMixin, TestCase):
    def test_authenticated_subscriptions(self):
        subscribe_url = reverse('group-subscribe', args=(self.group.slug,))
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
