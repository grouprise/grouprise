from features.groups import rules as groups
from features.memberships import predicates as memberships
import rules


@rules.predicate
def gestalt_is_member_of(user, group_gestalt):
    group, gestalt = group_gestalt
    return memberships.is_member_of(gestalt.user, group)


@rules.predicate
def has_group(user, group_gestalt):
    group, gestalt = group_gestalt
    return bool(group)


@rules.predicate
def is_closed(user, group_gestalt):
    group, gestalt = group_gestalt
    return groups.is_closed(user, group)


@rules.predicate
def is_member(user, association):
    if association.entity.is_group:
        return memberships.is_member_of(user, association.entity)
    else:
        return user.gestalt == association.entity


@rules.predicate
def is_member_of(user, group_gestalt):
    group, gestalt = group_gestalt
    return memberships.is_member_of(user, group)


@rules.predicate
def is_member_of_any_content_group(user, content):
    for group in content.groups.all():
        if memberships.is_member_of(user, group):
            return True
    return False


@rules.predicate
def is_public(user, association):
    return association.public
