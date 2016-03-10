from entities import rules as entities_rules
import rules

@rules.predicate
def content_is_public(user, content):
    return content.public

@rules.predicate
def is_content_author(user, content):
    return content.author == user.gestalt

rules.add_perm('content.view_content', content_is_public)
rules.add_perm('content.view_internal_content', rules.is_authenticated & entities_rules.is_group_member)
rules.add_perm('content.create_gestalt_content', rules.is_authenticated & entities_rules.is_gestalt)
rules.add_perm('content.create_group_content', rules.is_authenticated & entities_rules.is_group_member)
rules.add_perm('content.change_content', rules.is_authenticated & is_content_author)
