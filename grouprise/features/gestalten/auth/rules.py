import rules
from rules import is_authenticated

rules.add_perm("gestalten.login", ~is_authenticated)
rules.add_perm("account.logout", is_authenticated)
rules.add_perm("account.reset_password", ~is_authenticated)
