from . import models, notifications
from core import signals
from django import dispatch


@dispatch.receiver(signals.model_created, sender=models.Membership)
def membership_created(sender, instance, **kwargs):
    if instance.created_by != instance.member:
        notifications.MembershipCreated(membership=instance).send()
