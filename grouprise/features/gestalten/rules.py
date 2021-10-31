from rules import add_perm, always_allow, is_authenticated, predicate


@predicate
def is_self(user, gestalt):
    return user == gestalt.user


@predicate
def is_public(user, gestalt):
    return gestalt.public


add_perm("gestalten.view", is_public | (is_authenticated & is_self))
add_perm("gestalten.view_list", always_allow)

add_perm("gestalten.change", is_authenticated & is_self)
add_perm("gestalten.change_email", is_authenticated)
add_perm("gestalten.change_password", is_authenticated)

add_perm("gestalten.delete", is_authenticated)

add_perm("account.confirm", always_allow)
add_perm("account.set_password", is_authenticated)
add_perm("account.signup", ~is_authenticated)
