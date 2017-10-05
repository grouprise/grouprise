from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from features.associations import models as associations
from features.content import models as content
from features.subscriptions.notifications import ContentCreated
from . import models

post_create = Signal(providing_args=['instance'])


@receiver(post_create)
def content_created(sender, instance, **kwargs):
    ContentCreated.send_all(instance)
