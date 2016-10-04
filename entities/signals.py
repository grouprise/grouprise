from . import models
from datetime import date
from django import dispatch
from django.conf import settings
from django.contrib import auth
from django.contrib.sites import models as sites_models
from django.core import urlresolvers
from django.db.models import signals


@dispatch.receiver(signals.post_save, sender=auth.get_user_model())
def user_post_save(sender, instance, **kwargs):
    models.Gestalt.objects.get_or_create(user=instance)
