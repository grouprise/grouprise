from rules import add_perm, always_allow, is_authenticated, predicate

from features.memberships import predicates as memberships


@predicate
def is_closed(user, group):
    return group.closed


@predicate
def is_group(user, entity):
    return entity.is_group


add_perm('groups.create_group', always_allow)

add_perm('groups.view', always_allow)

add_perm('groups.view_list', always_allow)

add_perm('groups.change_group', is_authenticated & memberships.is_member_of)
