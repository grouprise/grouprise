import rules


@rules.predicate
def is_closed(user, group):
    return group.closed
