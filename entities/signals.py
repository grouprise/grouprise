from . import models
from datetime import date
from django.contrib import auth
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.db.models import signals
from django.dispatch import receiver
from django.utils import text


@receiver(signals.post_save, sender=auth.get_user_model())
def user_post_save(sender, instance, **kwargs):
    models.Gestalt.objects.get_or_create(user=instance)


@receiver(signals.pre_save, sender=models.Group)
def group_pre_save(sender, instance, **kwargs):
    group = instance
    if not group.slug:
        group.slug = text.slugify(group.name)
    if not group.address:
        group.address = group.name
    if not group.url:
        group.url = 'http://%(domain)s%(path)s' % {
                'domain': sites_models.Site.objects.get_current().domain,
                'path': urlresolvers.reverse('group', args=[group.slug]),
                }
    if not group.date_founded:
        group.date_founded = date.today()
