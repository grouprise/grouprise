from django.db.models.signals import post_delete, post_save
from django.db.utils import IntegrityError
from django.dispatch import receiver

from grouprise.features.memberships.models import Membership
from grouprise.features.subscriptions.models import Subscription


@receiver(post_save, sender=Membership)
def membership_saved(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        try:
            instance.member.subscriptions.create(
                subscribed_to_type=instance.group.content_type,
                subscribed_to_id=instance.group.id,
            )
        except IntegrityError:
            pass


@receiver(post_delete, sender=Membership)
def membership_deleted(sender, instance, **kwargs):
    try:
        subscription = instance.member.subscriptions.get(
            subscribed_to_type=instance.group.content_type,
            subscribed_to_id=instance.group.id,
        )
        subscription.delete()
    except Subscription.DoesNotExist:
        pass
