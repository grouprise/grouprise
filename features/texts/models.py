from django.contrib.contenttypes import (
        fields as contenttypes_fields, models as contenttypes_models)
from django.db import models
from django.utils import timezone


class Text(models.Model):
    container = contenttypes_fields.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(contenttypes_models.ContentType)

    author = models.ForeignKey('entities.Gestalt')
    time_created = models.DateTimeField(default=timezone.now)
    text = models.TextField()
