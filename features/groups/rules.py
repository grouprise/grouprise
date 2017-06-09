import rules


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
