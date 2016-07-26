from . import test_memberships as memberships, test_mixins as mixins
from utils import tests


class GroupAnonymous(
        memberships.OnlyJoinLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        tests.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        memberships.OnlyJoinLink,
        memberships.JoinAllowed,
        memberships.ResignForbidden,
        tests.AuthenticatedMixin, tests.GroupMixin, tests.Test):
    pass


class GroupMember(
        memberships.OnlyResignLink,
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        mixins.MemberMixin, tests.Test):
    pass
