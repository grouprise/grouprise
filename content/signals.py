from . import models
from django import dispatch
from django.db.models import signals
from django.utils import text


@dispatch.receiver(signals.pre_save, sender=models.Article)
def group_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = text.slugify(instance.title)
