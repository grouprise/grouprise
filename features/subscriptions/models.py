from django.contrib.contenttypes import (
        fields as contenttypes_fields,
        models as contenttypes_models)
from django.db import models


class Subscription(models.Model):
    content_type = models.ForeignKey(contenttypes_models.ContentType)
    object_id = models.PositiveIntegerField()
    subscribed_to = contenttypes_fields.GenericForeignKey()
    subscriber = models.ForeignKey('entities.Gestalt')
