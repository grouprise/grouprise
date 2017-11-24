import rules
from rules import is_authenticated

rules.add_perm('gestalten.login', ~rules.is_authenticated)
rules.add_perm('account.logout', rules.is_authenticated)
rules.add_perm('account.reset_password', ~rules.is_authenticated)

