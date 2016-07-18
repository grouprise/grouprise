from . import models
from content import rules as content
from features.memberships import rules as memberships
import rules


@rules.predicate
def is_subscribed_to(user, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance,
            subscriber=user.gestalt
            ).exists()


@rules.predicate
def is_subscriber(user, subscription):
    if subscription:
        return subscription.subscriber == user.gestalt
    return False


rules.add_perm(
        'subscriptions.create_content_subscription',
        rules.is_authenticated
        & content.is_permitted
        & ~content.is_author
        & ~content.is_recipient
        & ~memberships.is_member_of_content_group
        & ~is_subscribed_to)

rules.add_perm(
        'subscriptions.create_group_subscription',
        rules.is_authenticated
        & ~memberships.is_member_of
        & ~is_subscribed_to)

rules.add_perm(
        'subscriptions.delete_subscription',
        rules.is_authenticated
        & is_subscriber)
