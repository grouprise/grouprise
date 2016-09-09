from . import test_memberships as memberships, test_mixins as mixins
from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups


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
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        memberships.MemberListCreateLink,
        memberships.MemberCreateForbidden,
        mixins.MemberMixin, gestalten.OtherGestaltMixin, tests.Test):
    pass


class GroupClosedMember(
        memberships.OnlyResignLink,
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        memberships.MemberListCreateLink,
        memberships.MemberCreateAllowedWithEmail,
        memberships.MemberCreateSendsNotification,
        mixins.MemberMixin, groups.ClosedGroupMixin,
        gestalten.OtherGestaltMixin, tests.Test):
    pass
