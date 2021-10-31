from grouprise.core import tests
from grouprise.core.tests import get_url as u
from . import models


class JoinAllowed:
    def test_group_join(self):
        self.assertRequest(
            methods=[tests.HTTP_GET],
            url="join",
            key=self.group.slug,
            response={tests.HTTP_OK},
        )
        response = self.client.post(self.get_url("join", key=self.group.slug))
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertExists(models.Membership, group=self.group, member=self.gestalt)


class JoinForbidden:
    def test_group_join(self):
        self.assertRequest(
            methods=[tests.HTTP_GET, tests.HTTP_POST],
            url="join",
            key=self.group.slug,
            response={tests.HTTP_FORBIDDEN_OR_LOGIN},
        )


class JoinRedirectsToGroupPage:
    def test_group_join(self):
        r = self.client.get(u("join", self.group.slug))
        self.assertRedirects(r, self.group.get_absolute_url())
        r = self.client.post(u("join", self.group.slug))
        self.assertRedirects(r, self.group.get_absolute_url())


class MemberCreateAllowedWithEmail:
    def test_member_create(self):
        self.assertRequest(
            methods=[tests.HTTP_GET],
            url="member-create",
            key=self.group.pk,
            response={tests.HTTP_OK},
        )
        response = self.client.post(
            self.get_url("member-create", self.group.pk),
            {"member_email": self.other_gestalt.user.email},
        )
        self.assertRedirects(response, self.get_url("members", self.group.pk))
        self.assertExists(
            models.Membership, group=self.group, member=self.other_gestalt
        )


class MemberCreateSendsNotification:
    def test_member_create(self):
        self.client.post(
            self.get_url("member-create", self.group.pk),
            {"member_email": self.other_gestalt.user.email},
        )
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class MemberCreateForbidden:
    def test_member_create(self):
        self.assertRequest(
            methods=[tests.HTTP_GET, tests.HTTP_POST],
            url="member-create",
            key=self.group.pk,
            response={tests.HTTP_FORBIDDEN_OR_LOGIN},
        )


class MemberListCreateLink:
    def test_members(self):
        response = self.request(tests.HTTP_GET, url="members", key=self.group.pk)
        self.assertContainsLink(response, self.get_url("member-create", self.group.pk))


class MemberListNoCreateLink:
    def test_members(self):
        response = self.request(tests.HTTP_GET, url="members", key=self.group.pk)
        self.assertNotContainsLink(
            response, self.get_url("member-create", self.group.pk)
        )


class MemberListForbidden:
    def test_members(self):
        self.assertRequest(
            methods=[tests.HTTP_GET, tests.HTTP_POST],
            url="members",
            key=self.group.pk,
            response={tests.HTTP_FORBIDDEN_OR_LOGIN},
        )


class NoLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, self.get_url("join", self.group.slug))
        self.assertNotContainsLink(response, self.get_url("resign", self.group.pk))


class OnlyJoinLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertContainsLink(response, self.get_url("join", self.group.slug))
        self.assertNotContainsLink(response, self.get_url("resign", self.group.pk))


class OnlyResignLink:
    def test_group(self):
        response = self.client.get(self.group.get_absolute_url())
        self.assertNotContainsLink(response, self.get_url("join", self.group.slug))
        self.assertContainsLink(response, self.get_url("resign", self.group.pk))


class ResignAllowed:
    def test_group_resign(self):
        self.assertRequest(
            methods=[tests.HTTP_GET],
            url="resign",
            key=self.group.pk,
            response={tests.HTTP_OK},
        )
        response = self.client.post(self.get_url("resign", key=self.group.pk))
        self.assertRedirects(response, self.group.get_absolute_url())
        self.assertNotExists(models.Membership, group=self.group, member=self.gestalt)


class ResignForbidden:
    def test_group_resign(self):
        self.assertRequest(
            methods=[tests.HTTP_GET, tests.HTTP_POST],
            url="resign",
            key=self.group.pk,
            response={tests.HTTP_FORBIDDEN_OR_LOGIN},
        )
