from rules import add_perm, always_allow, is_authenticated, predicate

from features.memberships import predicates as memberships
from . import models

@predicate
def is_subscribed_to(user, model):
    return user.gestalt.subscriptions \
            .filter(subscribed_to_type=model.content_type, subscribed_to_id=model.id) \
            .exists()

add_perm(
        'subscriptions.create',
        ~is_authenticated
        | (is_authenticated
           & ~is_subscribed_to))

add_perm(
        'subscriptions.delete',
        is_authenticated
        & is_subscribed_to)
