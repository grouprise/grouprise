from . import (
        test_content as content_subscriptions,
        test_groups as group_subscriptions,
        test_mixins as mixins)
from core import tests
from features.comments import tests as comments
from features.content import tests as content
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class ContentAnonymous(
        content_subscriptions.OnlySubscribeLink,
        content_subscriptions.SubscribeAllowedWithEmail,
        content_subscriptions.UnsubscribeForbidden,
        content.ContentMixin, tests.Test):
    pass


class ContentAuthor(
        content_subscriptions.NoLink,
        content_subscriptions.SubscribeForbidden,
        content_subscriptions.UnsubscribeForbidden,
        gestalten.AuthenticatedMixin, content.ContentMixin, tests.Test):
    pass


class ContentNoAuthor(
        content_subscriptions.OnlySubscribeLink,
        content_subscriptions.SubscribeAllowed,
        content_subscriptions.UnsubscribeForbidden,
        content.NoAuthorContentMixin, tests.Test):
    pass


class ContentSubscribed(
        content_subscriptions.OnlyUnsubscribeLink,
        content_subscriptions.SubscribeForbidden,
        content_subscriptions.UnsubscribeAllowed,
        mixins.ContentSubscribedMixin, tests.Test):
    pass


class OtherContentSubscriber(
        comments.NotificationToOtherGestalt,
        mixins.OtherContentSubscriberMixin, tests.Test):
    """
    If an author creates a comment
    * a notification to content subscribers should be sent.
    """


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
