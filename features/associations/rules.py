from . import predicates
from content import predicates as content
import rules


rules.add_perm(
        'associations.create_content_group_membership',
        rules.is_authenticated
        & predicates.has_group
        & predicates.is_closed
        & predicates.is_member_of
        & ~predicates.gestalt_is_member_of)


# redefinition of content permissions

content_view_author = rules.permissions.permissions['content.view_author']

rules.remove_perm(
        'content.view_author')

rules.add_perm(
        'content.view_author',
        content_view_author
        | (content.is_permitted
           & rules.is_authenticated
           & predicates.is_member_of_any_content_group))
