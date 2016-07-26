from . import models
from utils import tests


class JoinAllowed:
    def test_group_join(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='join', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='join', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
        self.assertExists(
                models.Membership,
                group=self.group, member=self.gestalt)


class JoinForbidden:
    def test_group_join(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='join', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class MemberCreateAllowed:
    def test_member_create(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='member-create', key=self.group.pk,
                response={tests.HTTP_OK})
        response = self.client.post(
                self.get_url('member-create', self.group.pk),
                {'member': self.other_gestalt.pk})
        self.assertRedirects(response, self.get_url('members', self.group.pk))
        self.assertExists(
                models.Membership,
                group=self.group, member=self.other_gestalt)


class MemberCreateForbidden:
    def test_member_create(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='member-create', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class MemberListCreateLink:
    def test_members(self):
        response = self.request(
                tests.HTTP_GET, url='members', key=self.group.pk)
        self.assertContainsLink(response, 'member-create', self.group.pk)


class MemberListForbidden:
    def test_members(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='members', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})


class OnlyJoinLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertContainsLink(response, 'join', self.group.pk)
        self.assertNotContainsLink(
                response, 'resign', self.group.pk)


class OnlyResignLink:
    def test_group(self):
        response = self.request(
                tests.HTTP_GET, url='group', key=self.group.slug)
        self.assertNotContainsLink(response, 'join', self.group.pk)
        self.assertContainsLink(response, 'resign', self.group.pk)


class ResignAllowed:
    def test_group_resign(self):
        self.assertRequest(
                methods=[tests.HTTP_GET],
                url='resign', key=self.group.pk,
                response={tests.HTTP_OK})
        self.assertRequest(
                methods=[tests.HTTP_POST],
                url='resign', key=self.group.pk,
                response={tests.HTTP_REDIRECTS: ('group', self.group.slug)})
        self.assertNotExists(
                models.Membership,
                group=self.group, member=self.gestalt)


class ResignForbidden:
    def test_group_resign(self):
        self.assertRequest(
                methods=[tests.HTTP_GET, tests.HTTP_POST],
                url='resign', key=self.group.pk,
                response={tests.HTTP_FORBIDDEN_OR_LOGIN})
