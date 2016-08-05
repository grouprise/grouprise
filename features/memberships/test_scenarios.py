from . import test_memberships as memberships, test_mixins as mixins
from utils import tests


class GroupAnonymous(
        memberships.OnlyJoinLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        tests.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        memberships.OnlyJoinLink,
        memberships.JoinAllowed,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        tests.AuthenticatedMixin, tests.GroupMixin, tests.Test):
    pass


class GroupClosed(
        memberships.NoLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        tests.AuthenticatedMixin, tests.ClosedGroupMixin, tests.Test):
    pass


class GroupMember(
        memberships.OnlyResignLink,
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        memberships.MemberListCreateLink,
        memberships.MemberCreateAllowedWithEmail,
        mixins.MemberMixin, tests.OtherGestaltMixin, tests.Test):
    pass
