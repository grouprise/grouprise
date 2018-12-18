import django.db.models.signals
from django.dispatch import receiver

from features.contributions.tasks import send_contribution_notifications


post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    send_contribution_notifications(instance)
