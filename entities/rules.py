from rules import add_perm, always_allow, is_authenticated, predicate


@predicate
def is_group_member(user, group):
    return group.membership_set.filter(gestalt__user=user).exists()


add_perm('entities.view_gestalt', always_allow)
add_perm('entities.change_gestalt', is_authenticated)

add_perm('entities.view_group', always_allow)
add_perm('entities.change_group', is_authenticated & is_group_member)
