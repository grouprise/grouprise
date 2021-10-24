from grouprise.features.gestalten import models
from django import dispatch
from django.contrib import auth
from django.db.models import signals


@dispatch.receiver(signals.post_save, sender=auth.get_user_model())
def user_post_save(sender, instance, raw=False, **kwargs):
    if not raw:
        models.Gestalt.objects.get_or_create(user=instance)
