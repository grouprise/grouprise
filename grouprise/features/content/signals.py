from datetime import timedelta

from django.dispatch import receiver, Signal
from django.utils.timezone import now

from grouprise.core.tasks import auto_task

post_create = Signal(providing_args=['instance'])


@receiver(post_create)
def content_created(sender, instance, **kwargs):
    if now() - instance.versions.last().time_created < timedelta(weeks=1):
        auto_task(instance)
