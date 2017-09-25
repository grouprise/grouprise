from rules import add_perm, is_authenticated, predicate


@predicate
def is_conversation(user, contribution):
    return contribution.container.is_conversation


@predicate
def is_creator(user, contribution):
    return contribution.author == user.gestalt


add_perm('contributions.delete', ~is_conversation & is_authenticated & is_creator)
