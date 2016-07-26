from . import test_groups as group_subscriptions, test_mixins as mixins
from utils import tests


class Anonymous(
        group_subscriptions.OnlySubscribeLinkMixin,
        group_subscriptions.SubscribeForbiddenMixin,
        group_subscriptions.UnsubscribeForbiddenMixin,
        tests.GroupMixin, tests.Test):
    pass


class Authenticated(
        group_subscriptions.OnlySubscribeLinkMixin,
        group_subscriptions.SubscribeAllowedMixin,
        group_subscriptions.UnsubscribeForbiddenMixin,
        tests.AuthenticatedMixin, tests.GroupMixin, tests.Test):
    pass


class Member(
        group_subscriptions.NoLinkMixin,
        group_subscriptions.SubscribeForbiddenMixin,
        group_subscriptions.UnsubscribeForbiddenMixin,
        tests.MemberMixin, tests.Test):
    pass


class GroupSubscribed(
        group_subscriptions.OnlyUnsubscribeLinkMixin,
        group_subscriptions.SubscribeForbiddenMixin,
        group_subscriptions.UnsubscribeAllowedMixin,
        mixins.GroupSubscribedMixin, tests.Test):
    pass


class GroupSubscribedMember(
        group_subscriptions.OnlyUnsubscribeLinkMixin,
        group_subscriptions.SubscribeForbiddenMixin,
        group_subscriptions.UnsubscribeAllowedMixin,
        mixins.GroupSubscribedMixin, tests.MemberMixin, tests.Test):
    pass
