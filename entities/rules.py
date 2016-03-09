import rules

@rules.predicate
def is_gestalt(user, gestalt):
    return user == gestalt.user

@rules.predicate
def is_group_member(user, group):
    return group.members.filter(user=user).exists()

@rules.predicate
def is_group_membership(user, membership):
    return membership.gestalt == user.gestalt if membership else False

rules.add_perm('entities.view_gestalt', rules.always_allow)
rules.add_perm('entities.change_gestalt', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.mail_gestalt', rules.is_authenticated & ~is_gestalt)

rules.add_perm('entities.view_group', rules.always_allow)
rules.add_perm('entities.create_group', rules.is_authenticated)
rules.add_perm('entities.change_group', rules.is_authenticated & is_group_member)
rules.add_perm('entities.create_group_membership', rules.is_authenticated & ~is_group_member)
rules.add_perm('entities.delete_group_membership', rules.is_authenticated & is_group_membership)
