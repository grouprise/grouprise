from django import test
from django.contrib import auth
from django.core import urlresolvers
from entities import models as entities_models
from features.memberships import models as memberships_models


class GroupSubscription(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group1 = entities_models.Group.objects.create(name='Test1')

    def setUp(self):
        self.client = test.Client()

    def get_subscribe_link(self, group):
        return 'href="{}"'.format(
                urlresolvers.reverse(
                    'group-subscribe', args=[group.pk]))

    def test_group_page(self):
        response = self.client.get(self.group1.get_absolute_url())
        self.assertContains(response, self.get_subscribe_link(self.group1))


class AuthenticatedGroupSubscription(GroupSubscription):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group2 = entities_models.Group.objects.create(name="Test2")
        cls.gestalt1 = auth.get_user_model().objects.create(
                email='test@example.org').gestalt
        cls.membership1 = memberships_models.Membership.objects.create(
                group=cls.group2, member=cls.gestalt1)

    def setUp(self):
        super().setUp()
        self.client.force_login(self.gestalt1.user)

    def test_member_group_page(self):
        response = self.client.get(self.group2.get_absolute_url())
        self.assertNotContains(response, self.get_subscribe_link(self.group2))
