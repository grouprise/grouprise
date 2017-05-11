import rules

from features.associations import predicates as associations


@rules.predicate
def has_voted(user, association):
    return association.container.options.filter(vote__voter__user=user).exists()


rules.add_perm(
        'polls.vote',
        (associations.is_public | associations.is_member)
        & ~has_voted,
        )
