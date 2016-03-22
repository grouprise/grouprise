from . import models
from django import dispatch
from django.db.models import signals
from django.utils import text


@dispatch.receiver(signals.pre_save, sender=models.Article)
@dispatch.receiver(signals.pre_save, sender=models.Event)
@dispatch.receiver(signals.pre_save, sender=models.Gallery)
def group_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = text.slugify(instance.title)
