from django.contrib import auth
from django.db.models import signals
from django.dispatch import receiver

from . import models


@receiver(signals.post_save, sender=auth.get_user_model())
def user_post_save(sender, instance, **kwargs):
    models.Gestalt.objects.get_or_create(user=instance)
