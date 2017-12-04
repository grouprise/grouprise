from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from core import tests
from features.gestalten import tests as gestalten
from features.gestalten.tests import AuthenticatedMixin
from features.memberships.test_mixins import AuthenticatedMemberMixin
from .. import models
from .mixins import GroupMixin


class HasSidebarAndGroupsLinks:
    def test_links(self):
        response = self.client.get(self.get_url('index'))
        self.assertContainsLink(response, self.get_url('group-create'))
        response = self.client.get(self.get_url('group-index'))
        self.assertContainsLink(response, self.get_url('group-create'))


class CreateIsAllowed:
    def test_create(self):
        self.assertRequest(url='group-create', response={tests.HTTP_OK})
        response = self.client.post(
                self.get_url('group-create'), {'name': 'Test'})
        group = self.assertExists(models.Group, name='Test')
        self.assertRedirects(response, group.get_absolute_url())


class CreateAnonymous(
        HasSidebarAndGroupsLinks,
        CreateIsAllowed,
        tests.Test):
    """
    If an anonymous user wants to create a group:
    * there is a link in the sidebar and on the groups page
    * which renders a form
    * which on submission creates a group
    """


class CreateAuthenticated(
        HasSidebarAndGroupsLinks,
        CreateIsAllowed,
        gestalten.AuthenticatedMixin, tests.Test):
    """
    If a gestalt wants to create a group:
    * there is a link in the sidebar and on the groups page
    * which renders a form
    * which on submission creates a group
    """


class Settings(GroupMixin, TestCase):
    def test_group_settings(self):
        settings_url = '{}?group={}'.format(reverse('group-settings'), self.group.slug)

        # general group settings not accessible
        r = self.client.get(self.group.get_absolute_url())
        self.assertNotContains(r, 'href="{}"'.format(settings_url))
        r = self.client.get(settings_url)
        self.assertEqual(r.status_code, 302)


class AuthenticatedSettings(AuthenticatedMixin, GroupMixin, TestCase):
    def test_auth_group_settings(self):
        ms_settings_url = '{}?group={}'.format(
                reverse('subscriptions-memberships-settings'), self.group.slug)

        # access membership and subscription settings
        r = self.client.get(self.group.get_absolute_url())
        self.assertContains(r, 'href="{}"'.format(ms_settings_url))
        r = self.client.get(ms_settings_url)
        self.assertEqual(r.status_code, 200)


class AuthenticatedMemberSettings(AuthenticatedMemberMixin, TestCase):
    def test_member_group_settings(self):
        settings_url = '{}?group={}'.format(reverse('group-settings'), self.group.slug)

        # general group settings accessible
        r = self.client.get(self.group.get_absolute_url())
        self.assertContains(r, 'href="{}"'.format(settings_url))
        r = self.client.get(settings_url)
        self.assertEqual(r.status_code, 200)

        # save form with changed values
        r = self.client.post(settings_url, {'name': 'Changed Name', 'slug': 'changed-slug'})
        self.group.refresh_from_db()
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertEqual(self.group.name, 'Changed Name')
        self.assertEqual(self.group.slug, 'changed-slug')

    def test_member_group_image_settings(self):
        settings_url = '{}?group={}'.format(reverse('group-settings'), self.group.slug)
        image_settings_url = '{}?group={}'.format(
                reverse('group-image-settings'), self.group.slug)

        # check image setting availability
        r = self.client.get(settings_url)
        self.assertContains(r, 'href="{}"'.format(image_settings_url))
        r = self.client.get(image_settings_url)
        self.assertEqual(r.status_code, 200)
