import rules


@rules.predicate
def is_closed(user, group):
    return group.closed


rules.add_perm(
        'groups.create_group',
        rules.always_allow)

rules.add_perm(
        'entities.view_group',
        rules.always_allow)
