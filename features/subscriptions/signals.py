from django.dispatch import receiver

import features
from . import notifications


@receiver(features.content.signals.post_create)
def content_created(sender, instance, **kwargs):
    notifications.ContentCreated.send_all(instance)


@receiver(features.contributions.signals.post_create)
def contribution_created(sender, instance, **kwargs):
    notifications.ContributionCreated.send_all(instance)
