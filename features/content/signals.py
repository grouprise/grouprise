import django.db.models.signals
from django.dispatch import receiver

from features.associations import models as associations
from . import models, notifications


@receiver(django.db.models.signals.post_save, sender=associations.Association)
def send_content_notification(sender, instance, created, **kwargs):
    if created and instance.container_type == models.Content.content_type:
        notifications.ContentAssociated(instance=instance).send()
