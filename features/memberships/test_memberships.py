from . import models
from utils import tests


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
