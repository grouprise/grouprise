from . import models, notifications
from core import signals
from features.groups import models as groups


def add_first_member(group):
    if group.gestalt_created:
        models.Membership.objects.create(
                created_by=group.gestalt_created,
                group=group, member=group.gestalt_created)


def creator_is_not_member(membership):
    return membership.created_by != membership.member


connections = [
    signals.connect_action(
        signals.model_created, add_first_member,
        senders=[groups.Group],
        ),
    signals.connect_notification(
        signals.model_created, notifications.MembershipCreated,
        instance='membership',
        predicate=creator_is_not_member,
        senders=[models.Membership],
        ),
    ]
