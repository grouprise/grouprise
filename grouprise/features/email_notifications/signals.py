from datetime import timedelta

from django.dispatch import receiver
from django.utils.timezone import now

from grouprise.core.signals import post_create
from grouprise.core.tasks import auto_task
from grouprise.features.content.models import Content


@receiver(post_create)
def content_or_contribution_created(sender, instance, raw=False, **kwargs):
    if raw:
        # do not send notifications in case of loading a fixture
        pass
    elif isinstance(instance, Content):
        if now() - instance.versions.last().time_created < timedelta(weeks=1):
            auto_task(instance)
    else:
        auto_task(instance)
