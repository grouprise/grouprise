import rules
from rules import is_authenticated

from grouprise.features.associations import (
    models as associations_models,
    predicates as associations_rules,
)
from grouprise.features.gestalten.rules import is_self as is_gestalt
from grouprise.features.memberships import predicates as memberships


@rules.predicate
def can_view(user, association):
    return (
        associations_models.Association.objects.can_view(user, container="content")
        .filter(pk=association.pk)
        .exists()
    )


@rules.predicate
def is_member_of_associated_group(user, content):
    for group in content.get_associated_groups():
        if memberships.is_member_of(user, group):
            return True
    return False


rules.add_perm("content.list", rules.always_allow)

rules.add_perm("content.view", can_view)

rules.add_perm("content.comment", rules.is_authenticated & can_view)

rules.add_perm("content.create", rules.is_authenticated)

rules.add_perm("content.create_for_gestalt", is_authenticated & is_gestalt)

rules.add_perm(
    "content.group_create", rules.is_authenticated & memberships.is_member_of
)

rules.add_perm("content.change", rules.is_authenticated & associations_rules.is_member)
