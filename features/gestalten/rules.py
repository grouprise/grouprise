import rules
from rules import is_authenticated


@rules.predicate
def is_gestalt(user, gestalt):
    return user == gestalt.user


@rules.predicate
def is_public(user, gestalt):
    return gestalt.public


rules.add_perm('gestalten.view', is_public | (is_authenticated & is_gestalt))

rules.add_perm('entities.change_gestalt', rules.is_authenticated & is_gestalt)

rules.add_perm('gestalten.view_list', rules.always_allow)

rules.add_perm('gestalten.login', ~rules.is_authenticated)
