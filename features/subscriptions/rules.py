from . import models
from content import rules as content
from features.associations import rules as associations
from features.memberships import rules as memberships
import rules


@rules.predicate
def has_external_content_unsubscription_for(user, group):
    return models.Subscription.objects.filter(
            subscribed_to=group,
            subscriber=user.gestalt,
            unsubscribe=True,
            ).exists()


@rules.predicate
def is_subscribed_to(user, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance,
            subscriber=user.gestalt,
            unsubscribe=False,
            ).exists()


@rules.predicate
def is_subscriber(user, subscription):
    if subscription:
        return (
                not subscription.unsubscribe 
                and subscription.subscriber == user.gestalt)
    return False


rules.add_perm(
        'subscriptions.create_content_subscription',
        ~rules.is_authenticated
        | (rules.is_authenticated
           & content.is_permitted
           & ~content.is_author
           & ~content.is_recipient
           & ~associations.is_member_of_any_content_group
           & ~is_subscribed_to))

rules.add_perm(
        'subscriptions.create_external_content_unsubscription',
        rules.is_authenticated
        & memberships.is_member_of
        & ~has_external_content_unsubscription_for)

rules.add_perm(
        'subscriptions.create_group_subscription',
        ~rules.is_authenticated
        | (rules.is_authenticated
           & ~memberships.is_member_of
           & ~is_subscribed_to
           & rules.always_allow))

rules.add_perm(
        'subscriptions.delete_subscription',
        rules.is_authenticated
        & is_subscriber)
