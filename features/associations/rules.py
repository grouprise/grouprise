from . import predicates
import rules

rules.add_perm(
        'associations.create_content_group_membership',
        rules.is_authenticated
        & predicates.has_group
        & predicates.is_closed
        & predicates.is_member_of
        & ~predicates.gestalt_is_member_of)
