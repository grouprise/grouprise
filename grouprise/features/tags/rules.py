import rules

rules.add_perm("tags.view", rules.always_allow)

rules.add_perm("tags.tag_group", rules.is_authenticated)
