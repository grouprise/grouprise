from django.contrib.contenttypes import (
        fields as contenttypes_fields, models as contenttypes_models)
from django.db import models
from django.utils import timezone


class Authorship(models.Model):
    author = models.ForeignKey('gestalten.Gestalt')
    text = models.ForeignKey('Text', related_name='authorships')
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('time_created',)


class Text(models.Model):
    container = contenttypes_fields.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(contenttypes_models.ContentType)

    authors = models.ManyToManyField(
            to='gestalten.Gestalt', through='Authorship', related_name='texts')
    text = models.TextField()

    class Meta:
        ordering = ('authorships__time_created',)

    def get_unique_id(self):
        return '{}.{}.text.{}'.format(self.container_type, self.container.id, self.id)
