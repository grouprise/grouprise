import rules

from features.memberships import predicates as memberships


@rules.predicate
def is_closed(user, group):
    return group.closed


@rules.predicate
def is_group(user, entity):
    return entity.is_group


rules.add_perm(
        'groups.create_group',
        rules.always_allow)

rules.add_perm(
        'entities.view_group',
        rules.always_allow)

rules.add_perm(
        'groups.view_list',
        rules.always_allow)

rules.add_perm(
        'groups.change_group',
        rules.is_authenticated
        & memberships.is_member_of)
