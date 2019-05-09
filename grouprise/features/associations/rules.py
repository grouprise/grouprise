from rules import add_perm, is_authenticated, predicate


@predicate
def is_creator(user, association):
    return association.container.versions.first().author == user.gestalt


add_perm('associations.delete', is_authenticated & is_creator)
