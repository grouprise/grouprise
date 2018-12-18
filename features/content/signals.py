from datetime import timedelta

from django.dispatch import receiver, Signal
from django.utils.timezone import now

from features.content.tasks import send_content_notifications

post_create = Signal(providing_args=['instance'])


@receiver(post_create)
def content_created(sender, instance, **kwargs):
    if now() - instance.versions.last().time_created < timedelta(weeks=1):
        send_content_notifications(instance)
