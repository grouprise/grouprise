from . import predicates
import rules

rules.add_perm('content.view_content_list', rules.always_allow)
rules.add_perm('content.view_event_day', rules.always_allow)
rules.add_perm('content.view_help', rules.always_allow)

rules.add_perm('content.view_author', predicates.is_permitted & (
    ~predicates.is_group_content | ~predicates.is_public | (
        rules.is_authenticated & predicates.is_author)))
