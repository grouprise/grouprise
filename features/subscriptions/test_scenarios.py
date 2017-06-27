from . import (
        test_content as content_subscriptions,
        test_groups as group_subscriptions,
        test_mixins as mixins)
from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups
from features.memberships import test_mixins as memberships


class AllContentUnsubscribed(
        content_subscriptions.AllContentUnsubscribeForbidden,
        # content.NoNotification,
        mixins.AllContentUnsubscribedMixin, gestalten.OtherGestaltMixin, tests.Test):
    """
    If a group member is unsubscribed from all content
    * all content unsubscription is forbidden
    * gestalt receives no notifications on content
    """


class ExternalConversationUnsubscribed(
        # content_subscriptions.DeleteExternalUnsubscriptionLink,
        content_subscriptions.ExternalUnsubscribeForbidden,
        # content_subscriptions.DeleteExternalUnsubscriptionAllowed,
        # comments.NoNotification,
        # conversations.NoNotificationOnExternalConversation,
        mixins.ExternalUnsubscribedMixin, gestalten.OtherGestaltMixin, tests.Test):
    """
    If a group member is unsubscribed from external conversations
    * external unsubscription is forbidden
    * gestalt receives no notifications on external conversations
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
