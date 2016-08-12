from content import rules as content
from features.groups import rules as groups
from features.memberships import rules as memberships
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
def is_member_of(user, group_gestalt):
    group, gestalt = group_gestalt
    return memberships.is_member_of(user, group)


@rules.predicate
def is_member_of_any_content_group(user, content):
    for group in content.groups.all():
        if memberships.is_member_of(user, group):
            return True
    return False


rules.add_perm(
        'associations.create_content_group_membership',
        rules.is_authenticated
        & has_group
        & is_closed
        & is_member_of
        & ~gestalt_is_member_of)


# redefinition of content permissions

content_view_author = rules.permissions.permissions['content.view_author']

rules.remove_perm(
        'content.view_author')

rules.add_perm(
        'content.view_author',
        content_view_author
        | (content.is_permitted
           & rules.is_authenticated
           & is_member_of_any_content_group))
