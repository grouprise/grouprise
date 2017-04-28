import django.db.models.signals
from django.dispatch import receiver

from features.associations import models as associations
from features.content import models as content
from . import notifications


@receiver(django.db.models.signals.post_save, sender=associations.Association)
def send_content_notification(sender, instance, created, **kwargs):
    if created and instance.container_type == content.Content.content_type and instance.public:
        notifications.ContentPublicallyAssociated(instance=instance).send()
