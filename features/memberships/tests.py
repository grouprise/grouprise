from django.core import mail
from django.urls import reverse
from django.test import TestCase

from core.models import PermissionToken
from features.memberships.test_mixins import MemberMixin
from . import models

TEST_EMAIL = 'test.membership@test.local'


class Membership(MemberMixin, TestCase):
    def test_memberships(self):
        # join form renders ok
        join_request_url = reverse('join-request', args=(self.group.slug,))
        r = self.client.get(join_request_url)
        self.assertEquals(r.status_code, 200)

        # join succeeds with email address
        r = self.client.post(join_request_url, {'member': TEST_EMAIL})
        self.assertRedirects(r, self.group.get_absolute_url())

        # email with link to join confirmation is sent
        token = PermissionToken.objects.get(feature_key='group-join')
        join_confirm_url = reverse('join-confirm', args=(token.secret_key,))
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(join_confirm_url in mail.outbox[0].body)

        # join confirmation page renders ok
        r = self.client.get(join_confirm_url)
        self.assertEquals(r.status_code, 200)

        # join confirmation creates membership
        num_memberships = models.Membership.objects.count()
        r = self.client.post(join_confirm_url)
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertEqual(models.Membership.objects.count(), num_memberships+1)

        # cleanup
        mail.outbox = []

        # member gets notified on group content
        self.client.force_login(self.gestalt.user)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test', 'public': True})
        self.assertTrue(mail.outbox)
        for email_obj in mail.outbox:
            if email_obj.to[0].find(TEST_EMAIL) >= 0:
                break
        self.assertTrue(email_obj.to[0].find(TEST_EMAIL) >= 0)

        # cleanup
        mail.outbox = []
        self.client.logout()

        # notification contains link to resign form
        resign_request_url = reverse('resign-request', args=(self.group.pk,))
        self.assertTrue(resign_request_url in email_obj.body)

        # resign form renders ok
        r = self.client.get(resign_request_url)
        self.assertEquals(r.status_code, 200)

        # resign succeeds with email address
        r = self.client.post(resign_request_url, {'member': TEST_EMAIL})
        self.assertRedirects(r, self.group.get_absolute_url())

        # member gets email with link to resign confirmation
        token = PermissionToken.objects.get(feature_key='group-resign')
        resign_confirm_url = reverse('resign-confirm', args=(token.secret_key,))
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(resign_confirm_url in mail.outbox[0].body)

        # resign confirmation page renders ok
        r = self.client.get(resign_confirm_url)
        self.assertEquals(r.status_code, 200)

        # resign confirmation removes membership
        num_memberships = models.Membership.objects.count()
        r = self.client.post(resign_confirm_url)
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertEqual(models.Membership.objects.count(), num_memberships-1)
