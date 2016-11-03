from . import predicates
from features.associations import predicates as associations
import rules


rules.add_perm('content.view_content_list', rules.always_allow)
rules.add_perm('content.view_event_day', rules.always_allow)
rules.add_perm('content.view_help', rules.always_allow)

rules.add_perm('content.view_content', predicates.is_permitted)
rules.add_perm('content.view_author', predicates.is_permitted & (
    ~predicates.is_group_content | ~predicates.is_public | (
        rules.is_authenticated & predicates.is_author)))
rules.add_perm('content.create_content', rules.is_authenticated)
rules.add_perm('content.change_content', rules.is_authenticated & (
    predicates.is_author | associations.is_member_of_any_content_group))

rules.add_perm('content.create_comment', rules.is_authenticated & predicates.is_permitted)
