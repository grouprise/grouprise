from django.db.models.signals import post_delete, post_save
from django.db.utils import IntegrityError
from django.dispatch import receiver

from features.memberships.models import Membership
from features.subscriptions.models import Subscription
from . import models


@receiver(post_save, sender=Membership)
def membership_saved(sender, instance, created, **kwargs):
    if created:
        try:
            instance.member.subscriptions.create(
                    subscribed_to_type=instance.group.content_type,
                    subscribed_to_id=instance.group.id)
        except IntegrityError:
            pass


@receiver(post_delete, sender=Membership)
def membership_deleted(sender, instance, **kwargs):
    try:
        subscription = instance.member.subscriptions.get(
                subscribed_to_type=instance.group.content_type,
                subscribed_to_id=instance.group.id)
        subscription.delete()
    except Subscription.DoesNotExist:
        pass
