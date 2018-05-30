import django.db.models.signals
from django.dispatch import receiver

from . import notifications


post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    notifications.ContributionCreated.send_all(instance)
