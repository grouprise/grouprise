import rules


@rules.predicate
def is_creator(user, image):
    return user == image.creator.user


rules.add_perm("images.view", is_creator)
