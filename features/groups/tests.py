import core
from core import tests
from features.gestalten import tests as gestalten
from . import models


class GroupMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group = models.Group.objects.create(name='Test-Group')


class ClosedGroupMixin(GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.group.closed = True
        cls.group.save()


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


class TestUrls(core.tests.Test):
    def test_groups_404(self):
        r = self.client.get(self.get_url('group-update', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('group-avatar-update', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('group-logo-update', 0))
        self.assertEqual(r.status_code, 404)
