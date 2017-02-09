from core import models
from django.contrib.contenttypes import fields as contenttypes
from django.db import models as django


class Tag(django.Model):
    name = django.CharField(max_length=255)
    slug = models.AutoSlugField(populate_from='name', unique=True)

    def __str__(self):
        return self.name


class Tagged(django.Model):
    name = django.CharField(max_length=255)
    #tag = django.ForeignKey('Tag')

    tagged = contenttypes.GenericForeignKey('tagged_type', 'tagged_id')
    tagged_id = django.PositiveIntegerField()
    tagged_type = django.ForeignKey('contenttypes.ContentType')
