from rules import add_perm, is_authenticated, predicate


@predicate
def is_group_member(user, group):
    return group.membership_set.filter(gestalt__user=user).exists()


add_perm('entities.change_group', is_authenticated & is_group_member)
