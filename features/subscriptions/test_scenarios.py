import core
from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships
from . import (
        test_groups as group_subscriptions,
        test_mixins as mixins)


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


class TestUrls(core.tests.Test):
    def test_subscriptions_404(self):
        r = self.client.get(self.get_url('group-subscribe', 0))
        self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('group-unsubscribe', 0))
        self.assertEqual(r.status_code, 404)
