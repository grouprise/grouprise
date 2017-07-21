from . import models, test_memberships as memberships, test_mixins as mixins
from core import tests
from features.gestalten import tests as gestalten
from features.groups import models as groups_models, tests as groups


class CreatedGroupHasNoMembers:
    def test_members(self):
        self.client.post(self.get_url('group-create'), {'name': 'Test'})
        group = groups_models.Group.objects.get(name='Test')
        self.assertNotExists(models.Membership, group=group)


class CreatedGroupHasGestaltMember:
    def test_members(self):
        self.client.post(self.get_url('group-create'), {'name': 'Test'})
        group = groups_models.Group.objects.get(name='Test')
        self.assertExists(models.Membership, group=group, member=self.gestalt)


class GroupAnonymous(
        memberships.OnlyJoinLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        groups.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        memberships.OnlyJoinLink,
        memberships.JoinAllowed,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        gestalten.AuthenticatedMixin, groups.GroupMixin, tests.Test):
    pass


class GroupClosed(
        memberships.NoLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        gestalten.AuthenticatedMixin, groups.ClosedGroupMixin, tests.Test):
    pass


class GroupMember(
        memberships.OnlyResignLink,
        memberships.JoinRedirectsToGroupPage,
        memberships.ResignAllowed,
        memberships.MemberListNoCreateLink,
        memberships.MemberCreateForbidden,
        mixins.AuthenticatedMemberMixin, gestalten.OtherGestaltMixin, tests.Test):
    pass


class GroupClosedMember(
        memberships.OnlyResignLink,
        memberships.JoinRedirectsToGroupPage,
        memberships.ResignAllowed,
        memberships.MemberListCreateLink,
        memberships.MemberCreateAllowedWithEmail,
        memberships.MemberCreateSendsNotification,
        mixins.AuthenticatedMemberMixin, groups.ClosedGroupMixin,
        gestalten.OtherGestaltMixin, tests.Test):
    pass


class AnonymousUserCreatesGroup(
        CreatedGroupHasNoMembers,
        tests.Test):
    """
    If an anonymous user creates a group:
    * it has no members
    """


class GestaltCreatesGroup(
        CreatedGroupHasGestaltMember,
        gestalten.AuthenticatedMixin, tests.Test):
    """
    If a gestalt wants to create a group:
    * it has the gestalt as a member
    """
