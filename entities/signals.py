from . import models
from datetime import date
from django.conf import settings
from django.contrib import auth
from django.contrib.sites import models as sites_models
from django.core import mail, urlresolvers
from django.db.models import signals
from django import dispatch
from utils import text


@dispatch.receiver(signals.post_save, sender=models.GestaltContent)
@dispatch.receiver(signals.post_save, sender=models.GroupContent)
def content_post_save(sender, instance, created, **kwargs):
    if created:
        group = None
        recipients = set()
        if sender == models.GestaltContent:
            recipients |= {instance.gestalt}
        elif sender == models.GroupContent:
            group = instance.group
            recipients |= set(instance.group.members.exclude(pk=instance.content.author.pk))
            if instance.content.public:
                recipients |= set(instance.group.attendees.all())
        instance.content.notify(recipients)


@dispatch.receiver(signals.pre_save, sender=models.Group)
def group_pre_save(sender, instance, **kwargs):
    group = instance
    if not group.slug:
        group.slug = text.slugify(models.Group, 'slug', group.name)
    if not group.address:
        group.address = group.name
    if not group.url:
        group.url = '{protocol}://{domain}{path}'.format(
                protocol=settings.HTTP_PROTOCOL,
                domain=sites_models.Site.objects.get_current().domain,
                path=urlresolvers.reverse('group', args=[group.slug]),
                )
    if not group.date_founded:
        group.date_founded = date.today()


@dispatch.receiver(signals.post_save, sender=auth.get_user_model())
def user_post_save(sender, instance, **kwargs):
    models.Gestalt.objects.get_or_create(user=instance)
