from . import models
from django import dispatch
from django.conf import settings
from django.db.models import signals
from django.utils import module_loading
from entities import models as entities_models
from utils import text


@dispatch.receiver(signals.pre_save, sender=models.Article)
@dispatch.receiver(signals.pre_save, sender=models.Event)
@dispatch.receiver(signals.pre_save, sender=models.Gallery)
def content_pre_save(sender, instance, **kwargs):
    if instance.public and not instance.slug:
        instance.slug = text.slugify(models.Content, 'slug', instance.title)


@dispatch.receiver(signals.post_save, sender=models.Comment)
def comment_post_save(sender, instance, **kwargs):
    recipients = {instance.content.author}
    recipients |= set(instance.content.comment_authors.all())
    for gestalt in instance.content.gestalten.all():
        recipients |= {gestalt}
    for group in instance.content.groups.all():
        recipients |= set(entities_models.Gestalt.objects.filter(membership__group=group))
    # FIXME: What about private content?
    for notifier_str in settings.NOTIFIERS:
        Notifier = module_loading.import_string(notifier_str)
        recipients |= set(Notifier.get_recipients_for(instance.content))
    recipients.discard(instance.author)
    instance.notify(recipients)
