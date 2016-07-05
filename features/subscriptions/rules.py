from . import models
from content import rules as content_rules
from entities import rules as entities_rules
import rules


@rules.predicate
def is_subscribed_to(user, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance,
            subscriber=user.gestalt
            ).exists()


@rules.predicate
def is_subscriber(user, subscription):
    return subscription.subscriber == user.gestalt


rules.add_perm(
        'entities.create_content_subscription',
        rules.is_authenticated &
        ~content_rules.is_author &
        ~content_rules.is_group_member &
        ~is_subscribed_to)

rules.add_perm(
        'entities.create_group_subscription',
        rules.is_authenticated &
        ~entities_rules.is_group_member &
        ~is_subscribed_to)

rules.add_perm(
        'entities.delete_subscription',
        rules.is_authenticated & is_subscriber)
