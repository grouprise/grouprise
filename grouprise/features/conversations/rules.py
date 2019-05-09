from features.associations import models as associations
from features.gestalten import rules as gestalten
from features.memberships import predicates as memberships
import rules


@rules.predicate
def can_view(user, association):
    return associations.Association.objects.can_view(user, container='conversation') \
            .filter(pk=association.pk).exists()


rules.add_perm(
        'conversations.create_gestalt_conversation',
        rules.is_authenticated
        | gestalten.is_public
        )

rules.add_perm(
        'conversations.create_group_conversation',
        rules.always_allow)

rules.add_perm(
        'conversations.create_group_conversation_by_email',
        memberships.is_member_of)

rules.add_perm(
        'conversations.list',
        rules.always_allow)

rules.add_perm(
        'conversations.list_group',
        memberships.is_member_of)

rules.add_perm(
        'conversations.reply',
        can_view)

rules.add_perm(
        'conversations.view',
        can_view)
