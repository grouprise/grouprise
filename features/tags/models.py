import django
from django.contrib.contenttypes import fields as contenttypes
from django.db import models

from core.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    @classmethod
    def slugify(cls, name):
        return slugify(name)[:50]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return django.urls.reverse('tag', args=(self.slug,))


class Tagged(models.Model):
    class Meta:
        ordering = ('tag__name',)
        unique_together = ('tag', 'tagged_id', 'tagged_type',)

    tag = models.ForeignKey('Tag', related_name='tagged', on_delete=models.CASCADE)

    tagged = contenttypes.GenericForeignKey('tagged_type', 'tagged_id')
    tagged_id = models.PositiveIntegerField()
    tagged_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)

    def __str__(self):
        return "%s was tagged with '%s'" % (str(self.tagged), str(self.tag))
