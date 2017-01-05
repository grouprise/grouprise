from . import models
from django import dispatch
from django.db.models import signals
from utils import text


@dispatch.receiver(signals.pre_save, sender=models.Article)
@dispatch.receiver(signals.pre_save, sender=models.Event)
@dispatch.receiver(signals.pre_save, sender=models.Gallery)
def content_pre_save(sender, instance, **kwargs):
    if instance.public and not instance.slug:
        instance.slug = text.slugify(models.Content, 'slug', instance.title)
