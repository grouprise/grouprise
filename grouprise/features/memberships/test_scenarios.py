import grouprise.core
import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from grouprise.core import tests
from grouprise.features.groups import models as groups_models
from grouprise.features.groups.tests import mixins as groups

from . import models
from . import test_memberships as memberships
from . import test_mixins as mixins


class CreatedGroupHasNoMembers:
    def test_members(self):
        self.client.post(self.get_url("group-create"), {"name": "Test"})
        group = groups_models.Group.objects.get(name="Test")
        self.assertNotExists(models.Membership, group=group)


class CreatedGroupHasGestaltMember:
    def test_members(self):
        self.client.post(self.get_url("group-create"), {"name": "Test"})
        group = groups_models.Group.objects.get(name="Test")
        self.assertExists(models.Membership, group=group, member=self.gestalt)


class GroupAnonymous(
    memberships.OnlyJoinLink,
    memberships.JoinForbidden,
    memberships.ResignForbidden,
    memberships.MemberListForbidden,
    memberships.MemberCreateForbidden,
    groups.GroupMixin,
    tests.Test,
):
    pass


class GroupAuthenticated(
    memberships.OnlyJoinLink,
    memberships.JoinAllowed,
    memberships.ResignForbidden,
    memberships.MemberListForbidden,
    memberships.MemberCreateForbidden,
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    groups.GroupMixin,
    tests.Test,
):
    pass


class GroupClosed(
    memberships.NoLink,
    memberships.JoinForbidden,
    memberships.ResignForbidden,
    memberships.MemberListForbidden,
    memberships.MemberCreateForbidden,
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    groups.ClosedGroupMixin,
    tests.Test,
):
    pass


class GroupMember(
    # memberships.OnlyResignLink,
    memberships.JoinRedirectsToGroupPage,
    memberships.ResignAllowed,
    memberships.MemberListNoCreateLink,
    memberships.MemberCreateForbidden,
    mixins.AuthenticatedMemberMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
    tests.Test,
):
    pass


class GroupClosedMember(
    # memberships.OnlyResignLink,
    memberships.JoinRedirectsToGroupPage,
    memberships.ResignAllowed,
    memberships.MemberListCreateLink,
    memberships.MemberCreateAllowedWithEmail,
    memberships.MemberCreateSendsNotification,
    mixins.AuthenticatedMemberMixin,
    groups.ClosedGroupMixin,
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin,
    tests.Test,
):
    pass


class AnonymousUserCreatesGroup(CreatedGroupHasNoMembers, tests.Test):
    """
    If an anonymous user creates a group:
    * it has no members
    """


class GestaltCreatesGroup(
    CreatedGroupHasGestaltMember,
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    tests.Test,
):
    """
    If a gestalt wants to create a group:
    * it has the gestalt as a member
    """


class TestUrls(grouprise.core.tests.Test):
    def test_member_404(self):
        r = self.client.get(self.get_url("create-membership-application", 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url("accept-membership-application", 0))
        self.assertEqual(r.status_code, 404)


class AuthenticatedTestUrls(
    grouprise.features.gestalten.tests.mixins.AuthenticatedMixin,
    grouprise.core.tests.Test,
):
    def test_member_auth_404(self):
        # r = self.client.get(self.get_url('join', 0))
        # self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url("members", 0))
        self.assertEqual(r.status_code, 404)
        # r = self.client.get(self.get_url('member-create', 0))
        # self.assertEqual(r.status_code, 404)


class MemberTestUrls(mixins.AuthenticatedMemberMixin, grouprise.core.tests.Test):
    def test_member_member_404(self):
        r = self.client.get(self.get_url("resign", 0))
        self.assertEqual(r.status_code, 404)
