from django.dispatch import receiver

from core import signals
from features.groups import models as groups
from . import models, notifications


@receiver(signals.model_created, sender=groups.Group)
def add_first_member(sender, instance, **kwargs):
    group = instance
    if group.gestalt_created:
        models.Membership.objects.create(
                created_by=group.gestalt_created,
                group=group, member=group.gestalt_created)


@receiver(signals.model_created, sender=models.Membership)
def send_membership_notification(sender, instance, **kwargs):
    membership = instance
    if membership.created_by != membership.member:
        notifications.MembershipCreated(membership=membership).send()
