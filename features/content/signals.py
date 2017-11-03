from django.dispatch import receiver, Signal

import features
from . import notifications

post_create = Signal(providing_args=['instance'])


@receiver(post_create)
def content_created(sender, instance, **kwargs):
    notifications.ContentCreated.send_all(instance)
