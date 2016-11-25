import rules


def may_view(user, association):
    return False


rules.add_perm(
        'conversations.view',
        rules.is_authenticated
        & may_view) 
