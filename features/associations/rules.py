from rules import add_perm, is_authenticated, predicate

from . import predicates

@predicate
def is_creator(user, association):
    return association.container.versions.first().author == user.gestalt

add_perm(
        'associations.create_content_group_membership',
        is_authenticated
        & predicates.has_group
        & predicates.is_closed
        & predicates.is_member_of
        & ~predicates.gestalt_is_member_of)

add_perm('associations.delete', is_authenticated & is_creator)
