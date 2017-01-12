from django.contrib.contenttypes import fields as contenttypes
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=255)

    tagged = contenttypes.GenericForeignKey('tagged_type', 'tagged_id')
    tagged_id = models.PositiveIntegerField()
    tagged_type = models.ForeignKey('contenttypes.ContentType')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
