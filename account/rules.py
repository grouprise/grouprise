import rules

rules.add_perm('account.confirm', rules.always_allow)
rules.add_perm('account.login', ~rules.is_authenticated)
rules.add_perm('account.logout', rules.is_authenticated)
rules.add_perm('account.reset_password', ~rules.is_authenticated)
rules.add_perm('account.signup', ~rules.is_authenticated)
