from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from core.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def slugify(cls, name):
        return slugify(None, None, name, dodging=False)


class Tagged(models.Model):
    tag = models.ForeignKey('Tag', related_name='tagged')

    tagged = contenttypes.GenericForeignKey('tagged_type', 'tagged_id')
    tagged_id = models.PositiveIntegerField()
    tagged_type = models.ForeignKey('contenttypes.ContentType')

    class Meta:
        ordering = ('tag__name',)
