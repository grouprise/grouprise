from . import (
        test_content as content_subscriptions,
        test_groups as group_subscriptions,
        test_mixins as mixins)
from features.memberships import test_mixins as memberships
from utils import tests


class ContentAnonymous(
        content_subscriptions.OnlySubscribeLink,
        content_subscriptions.SubscribeForbidden,
        content_subscriptions.UnsubscribeForbidden,
        tests.ContentMixin, tests.Test):
    pass


class ContentAuthor(
        content_subscriptions.NoLink,
        content_subscriptions.SubscribeForbidden,
        content_subscriptions.UnsubscribeForbidden,
        tests.AuthenticatedMixin, tests.ContentMixin, tests.Test):
    pass


class ContentNoAuthor(
        content_subscriptions.OnlySubscribeLink,
        content_subscriptions.SubscribeAllowed,
        content_subscriptions.UnsubscribeForbidden,
        tests.NoAuthorContentMixin, tests.Test):
    pass


class ContentSubscribed(
        content_subscriptions.OnlyUnsubscribeLink,
        content_subscriptions.SubscribeForbidden,
        content_subscriptions.UnsubscribeAllowed,
        mixins.ContentSubscribedMixin, tests.Test):
    pass


class GroupAnonymous(
        group_subscriptions.OnlySubscribeLink,
        group_subscriptions.SubscribeAllowed,
        group_subscriptions.UnsubscribeForbidden,
        tests.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        group_subscriptions.OnlySubscribeLink,
        group_subscriptions.SubscribeAllowed,
        group_subscriptions.UnsubscribeForbidden,
        tests.AuthenticatedMixin, tests.GroupMixin, tests.Test):
    pass


class GroupMember(
        group_subscriptions.NoLink,
        group_subscriptions.SubscribeForbidden,
        group_subscriptions.UnsubscribeForbidden,
        memberships.MemberMixin, tests.Test):
    pass


class GroupSubscribed(
        group_subscriptions.OnlyUnsubscribeLink,
        group_subscriptions.SubscribeForbidden,
        group_subscriptions.UnsubscribeAllowed,
        mixins.GroupSubscribedMixin, tests.Test):
    pass


class GroupSubscribedMember(
        group_subscriptions.OnlyUnsubscribeLink,
        group_subscriptions.SubscribeForbidden,
        group_subscriptions.UnsubscribeAllowed,
        mixins.GroupSubscribedMixin, memberships.MemberMixin, tests.Test):
    pass
