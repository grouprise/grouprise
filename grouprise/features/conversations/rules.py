from grouprise.features.associations import models as associations
from grouprise.features.gestalten import rules as gestalten
from grouprise.features.groups.rules import is_closed
from grouprise.features.memberships.predicates import is_member_of
import rules


@rules.predicate
def can_view(user, association):
    return (
        associations.Association.objects.can_view(user, container="conversation")
        .filter(pk=association.pk)
        .exists()
    )


rules.add_perm(
    "conversations.create_gestalt_conversation",
    rules.is_authenticated | gestalten.is_public,
)

rules.add_perm("conversations.create_group_conversation", rules.always_allow)

rules.add_perm("conversations.create_group_conversation_by_email", is_member_of)

rules.add_perm(
    "conversations.create_group_conversation_with_membership_application",
    is_closed & ~is_member_of,
)

rules.add_perm("conversations.list_group", is_member_of)

rules.add_perm("conversations.reply", can_view)

rules.add_perm("conversations.view", can_view)
