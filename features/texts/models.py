from django.contrib.contenttypes import (
        fields as contenttypes_fields, models as contenttypes_models)
from django.db import models
from django.utils import timezone


class Text(models.Model):
    container = contenttypes_fields.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(contenttypes_models.ContentType)

    author = models.ForeignKey('gestalten.Gestalt', related_name='texts')
    time_created = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    class Meta:
        ordering = ('time_created',)

    def get_unique_id(self):
        return '{}.{}.text.{}'.format(self.container_type, self.container.id, self.id)
