from . import models
from content import rules as content
from features.groups import rules as groups
import rules
import rules.permissions


@rules.predicate
def is_member(user, membership):
    if membership:
        return membership.member == user.gestalt
    return False


@rules.predicate
def is_member_of(user, group):
    return models.Membership.objects.filter(
            group=group,
            member=user.gestalt
            ).exists()


@rules.predicate
def is_member_of_content_group(user, content):
    for group in content.groups.all():
        if is_member_of(user, group):
            return True
    return False


rules.add_perm(
        'memberships.join_group',
        rules.is_authenticated
        & ~is_member_of
        & ~groups.is_closed)

rules.add_perm(
        'memberships.create_membership',
        rules.is_authenticated
        & is_member_of)

rules.add_perm(
        'memberships.delete_membership',
        rules.is_authenticated
        & is_member)

rules.add_perm(
        'memberships.list_memberships',
        rules.is_authenticated
        & is_member_of)


# redefinition of content permissions

content_view_author = rules.permissions.permissions['content.view_author']

rules.remove_perm(
        'content.view_author')

rules.add_perm(
        'content.view_author',
        content_view_author
        | (content.is_permitted
           & rules.is_authenticated
           & is_member_of_content_group))


# redefinition of groups permissions

if rules.perm_exists('groups.change_group'):
    rules.remove_perm('groups.change_group')

rules.add_perm(
        'groups.change_group',
        rules.is_authenticated
        & is_member_of)
