from . import models
from django import dispatch
from django.db.models import signals
from django.utils import text


@dispatch.receiver(signals.pre_save, sender=models.Article)
@dispatch.receiver(signals.pre_save, sender=models.Event)
@dispatch.receiver(signals.pre_save, sender=models.Gallery)
def content_pre_save(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = text.slugify(instance.title)


@dispatch.receiver(signals.post_save, sender=models.Comment)
def comment_post_save(sender, instance, **kwargs):
    recipients = {instance.content.author}
    recipients |= set(instance.content.comment_authors.all())
    for group in instance.content.groups.all():
        recipients |= set(group.members.all())
    #recipients |= set(instance.attendees.all())
    recipients.discard(instance.author)
    instance.notify(recipients)
