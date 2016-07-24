from . import models
from django import test
from django.contrib import auth
from django.core import urlresolvers
from entities import models as entities_models
from features.memberships import models as memberships_models


class GroupSubscription(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group = entities_models.Group.objects.create(name='Test')

    def setUp(self):
        self.client = test.Client()

    def get_link(self, link_type, group):
        return 'href="{}"'.format(self.get_url(link_type, group))

    def get_url(self, link_type, group):
        return urlresolvers.reverse(
                'group-{}'.format(link_type), args=[group.pk])

    def test_group_page(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContains(response, self.get_link('subscribe', self.group))
        self.assertNotContains(
                response, self.get_link('unsubscribe', self.group))

    def test_subscribe(self):
        subscribe_url = self.get_url('subscribe', self.group)
        response = self.client.get(subscribe_url)
        self.assertRedirects(response, '{}?next={}'.format(
            urlresolvers.reverse('account_login'), subscribe_url))
        response = self.client.post(subscribe_url)
        self.assertRedirects(response, '{}?next={}'.format(
            urlresolvers.reverse('account_login'), subscribe_url))


class AuthenticatedGroupSubscription(GroupSubscription):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.member_group = entities_models.Group.objects.create(
                name="Member Test")
        cls.gestalt = auth.get_user_model().objects.create(
                email='test@example.org').gestalt
        memberships_models.Membership.objects.create(
                group=cls.member_group, member=cls.gestalt)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.gestalt.user)

    def test_member_group_page(self):
        response = self.client.get(self.member_group.get_absolute_url())
        self.assertNotContains(
                response, self.get_link('subscribe', self.member_group))
        self.assertNotContains(
                response, self.get_link('unsubscribe', self.member_group))

    def test_subscribe(self):
        response = self.client.get(self.get_url('subscribe', self.group))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.get_url('subscribe', self.group))
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertTrue(models.Subscription.objects.filter(
            subscribed_to=self.group, subscriber=self.gestalt))

    def test_member_subscribe(self):
        response = self.client.get(
                self.get_url('subscribe', self.member_group))
        self.assertEqual(response.status_code, 403)
        response = self.client.post(
                self.get_url('subscribe', self.member_group))
        self.assertEqual(response.status_code, 403)
