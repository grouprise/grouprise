from . import (
        test_groups as group_subscriptions,
        test_mixins as mixins)
from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class GroupAnonymous(
        group_subscriptions.OnlySubscribeLink,
        group_subscriptions.SubscribeAllowedWithEmail,
        group_subscriptions.UnsubscribeForbidden,
        gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        group_subscriptions.OnlySubscribeLink,
        group_subscriptions.SubscribeAllowed,
        group_subscriptions.UnsubscribeForbidden,
        gestalten.AuthenticatedMixin, groups.GroupMixin, tests.Test):
    pass


class GroupMember(
        group_subscriptions.NoLink,
        group_subscriptions.SubscribeRedirectToGroupPage,
        group_subscriptions.UnsubscribeForbidden,
        memberships.AuthenticatedMemberMixin, tests.Test):
    pass


class GroupSubscribed(
        group_subscriptions.OnlyUnsubscribeLink,
        group_subscriptions.SubscribeRedirectToGroupPage,
        group_subscriptions.UnsubscribeAllowed,
        mixins.GroupSubscribedMixin, tests.Test):
    pass


class GroupSubscribedMember(
        group_subscriptions.OnlyUnsubscribeLink,
        group_subscriptions.SubscribeRedirectToGroupPage,
        group_subscriptions.UnsubscribeAllowed,
        mixins.GroupSubscribedMixin, memberships.MemberMixin, tests.Test):
    pass
