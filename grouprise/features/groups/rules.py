from rules import add_perm, always_allow, is_authenticated, predicate

from grouprise.features.memberships import predicates as memberships


@predicate
def is_closed(user, group):
    return group.closed


@predicate
def is_group(user, entity):
    return entity.is_group


add_perm('groups.create_group', always_allow)
add_perm('groups.view', always_allow)
add_perm('groups.view_list', always_allow)
add_perm('groups.change', is_authenticated & memberships.is_member_of)
add_perm('groups.change_subscriptions_memberships', is_authenticated)
add_perm('groups.recommend', always_allow)
