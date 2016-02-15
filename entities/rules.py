import rules


@rules.predicate
def is_gestalt(user, gestalt):
    return user == gestalt.user

@rules.predicate
def is_group_member(user, group):
    return group.membership_set.filter(gestalt__user=user).exists()


rules.add_perm('entities.view_gestalt', rules.always_allow)
rules.add_perm('entities.change_gestalt', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.mail_gestalt', rules.is_authenticated & ~is_gestalt)

rules.add_perm('entities.view_group', rules.always_allow)
rules.add_perm('entities.change_group', rules.is_authenticated & is_group_member)
