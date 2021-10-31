from rules import add_perm, is_authenticated, predicate


@predicate
def is_subscribed(user, model):
    return user.gestalt.subscriptions.filter(
        subscribed_to_type=model.content_type, subscribed_to_id=model.id
    ).exists()


add_perm(
    "subscriptions.create", ~is_authenticated | (is_authenticated & ~is_subscribed)
)

add_perm("subscriptions.delete", is_authenticated & is_subscribed)

add_perm("subscriptions.delete_request", ~is_authenticated)
