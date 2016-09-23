from . import models
from features.memberships import rules as memberships_rules
import rules

@rules.predicate
def is_gestalt(user, gestalt):
    return gestalt and user == gestalt.user

@rules.predicate
def is_public(user, gestalt):
    return gestalt.public

rules.add_perm('entities.view_gestalt', is_public | is_gestalt)
rules.add_perm('entities.change_gestalt', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.create_gestalt_content', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.create_gestalt_message', rules.always_allow)
rules.add_perm('entities.mail_gestalt', rules.is_authenticated & ~is_gestalt)

rules.add_perm('entities.create_group_content', rules.is_authenticated & memberships_rules.is_member_of)
rules.add_perm('entities.create_group_message', rules.always_allow)

rules.add_perm('entities.view_imprint', rules.always_allow)
