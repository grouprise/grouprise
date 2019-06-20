import django.db.models.signals
from django.dispatch import receiver

from grouprise.core.tasks import auto_task

post_create = django.dispatch.Signal(providing_args=['instance'])


@receiver(post_create)
def contribution_created(sender, instance, **kwargs):
    auto_task(instance)
