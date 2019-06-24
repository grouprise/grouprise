from datetime import date, timedelta
from rules import add_perm, is_authenticated, predicate

from grouprise.features.memberships.models import Membership


@predicate
def is_creator(user, association):
    return association.container.versions.first().author == user.gestalt


@predicate
def is_long_standing_group_member(user, association):
    if not association.entity.is_group:
        return False
    membership = Membership.objects.filter(group=association.entity, member=user.gestalt) \
                                   .first()
    if not membership:
        return False
    return membership.date_joined < date.today() - timedelta(weeks=1)


add_perm('associations.delete',
         is_authenticated & (is_creator | is_long_standing_group_member))
