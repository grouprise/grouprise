from . import models, notifications
from django import dispatch
from django.db.models import signals


@dispatch.receiver(signals.post_save, sender=models.Membership)
def membership_post_save(sender, instance, created, **kwargs):
    if created and instance.created_by != instance.member:
        notifications.MembershipCreated(membership=instance).send()
