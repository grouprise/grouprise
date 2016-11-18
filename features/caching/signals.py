from content import models as content
from core import signals
from django.contrib import auth
from django.core import cache
from django.core.cache import utils
from entities import models as gestalten
from features.groups import models as groups
from features.memberships import models as memberships
from features.subscriptions import models as subscriptions
import itertools


def model_ids_including_none(model_class):
    return itertools.chain([''], model_class._default_manager.values_list('id', flat=True))


def invalidate_cache(fragment, *args):
    cache.cache.delete(utils.make_template_fragment_key(fragment, args))


def comments_count_changed(comment):
    invalidate_cache('conversation-preview', comment.content.id)
    for gestalt_id in model_ids_including_none(gestalten.Gestalt):
        invalidate_cache('content-detail', gestalt_id, comment.content.id)


def content_changed(content):
    invalidate_cache('content-preview', content.id)
    invalidate_cache('conversation-preview', content.id)
    for gestalt_id in model_ids_including_none(gestalten.Gestalt):
        invalidate_cache('content-detail', gestalt_id, content.id)


def gestalt_changed(gestalt):
    for group_id in model_ids_including_none(groups.Group):
        invalidate_cache('site-menu', gestalt.id, group_id)


def group_changed(group):
    invalidate_cache('sidebar-groups')
    for gestalt_id in model_ids_including_none(gestalten.Gestalt):
        invalidate_cache('group-header', gestalt_id, group.id)
        invalidate_cache('group-preview', gestalt_id, group.id)
        invalidate_cache('site-menu', gestalt_id, group.id)


def groups_count_changed(group):
    invalidate_cache('sidebar-groups')


def memberships_count_changed(membership):
    print('MEMBERSHIP', membership.group, membership.member)
    invalidate_cache('group-header', membership.member.id, membership.group.id)
    invalidate_cache('group-preview', membership.member.id, membership.group.id)
    for group_id in model_ids_including_none(groups.Group):
        invalidate_cache('site-menu', membership.member.id, group_id)


def subscriptions_count_changed(subscription):
    if type(subscription.subscribed_to) == content.Content:
        for gestalt_id in model_ids_including_none(gestalten.Gestalt):
            invalidate_cache('content-detail', gestalt_id, subscription.subscribed_to.id)
    if type(subscription.subscribed_to) == groups.Group:
        invalidate_cache(
                'group-header', subscription.subscriber.id, subscription.subscribed_to.id)
        invalidate_cache(
                'group-preview', subscription.subscriber.id, subscription.subscribed_to.id)


def user_changed(user):
    gestalt_changed(user.gestalt)


connections = [
    # comments
    signals.connect_action(
        signals.model_created,
        comments_count_changed,
        senders=[content.Comment]),

    signals.connect_action(
        signals.model_deleted,
        comments_count_changed,
        senders=[content.Comment]),

    # content
    signals.connect_action(
        signals.model_changed,
        content_changed,
        senders=[content.Article, content.Content, content.Event, content.Gallery]),

    # gestalten
    signals.connect_action(
        signals.model_changed,
        gestalt_changed,
        senders=[gestalten.Gestalt]),

    # groups
    signals.connect_action(
        signals.model_changed,
        group_changed,
        senders=[groups.Group]),

    signals.connect_action(
        signals.model_created,
        groups_count_changed,
        senders=[groups.Group]),

    signals.connect_action(
        signals.model_deleted,
        groups_count_changed,
        senders=[groups.Group]),

    # memberships
    signals.connect_action(
        signals.model_created,
        memberships_count_changed,
        senders=[memberships.Membership]),

    signals.connect_action(
        signals.model_deleted,
        memberships_count_changed,
        senders=[memberships.Membership]),

    # subscriptions
    signals.connect_action(
        signals.model_created,
        subscriptions_count_changed,
        senders=[subscriptions.Subscription]),

    signals.connect_action(
        signals.model_deleted,
        subscriptions_count_changed,
        senders=[subscriptions.Subscription]),

    # users
    signals.connect_action(
        signals.model_changed,
        user_changed,
        senders=[auth.get_user_model()]),
    ]
