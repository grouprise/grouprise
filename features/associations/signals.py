from django.db.models.signals import post_save
from django.dispatch import receiver

from features.associations import models as associations
from features.content import models as content
from features.subscriptions.notifications import ContentAssociated
from . import models


@receiver(post_save, sender=models.Association)
def association_saved(sender, instance, created, **kwargs):
    if created and not instance.container.is_conversation:
        ContentAssociated(instance).send()
