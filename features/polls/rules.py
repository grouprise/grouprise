import rules

from features.associations import predicates as associations


@rules.predicate
def has_voted(user, association):
    return association.container.options.filter(vote__voter=user.gestalt).exists()


rules.add_perm(
        'polls.vote',
        (associations.is_public
            | (rules.is_authenticated
                & associations.is_member))
        & (~rules.is_authenticated
            | ~has_voted)
        )
