from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from django.db.models import Q
from core.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def slugify(cls, name):
        return slugify(name)


class Tagged(models.Model):
    tag = models.ForeignKey('Tag', related_name='tagged')

    tagged = contenttypes.GenericForeignKey('tagged_type', 'tagged_id')
    tagged_id = models.PositiveIntegerField()
    tagged_type = models.ForeignKey('contenttypes.ContentType')

    @classmethod
    def get_tagged_query(cls, tag, model):
        content_type = contenttypes.ContentType.objects.get_for_model(model)
        tagged_objects = Tagged.objects.filter(tagged_type=content_type, tag=tag)
        model_ids = list(map(lambda tagged: tagged.tagged_id, tagged_objects))
        return Q(pk__in=model_ids)

    def __repr__(self):
        return "%s was tagged with '%s'" % (str(self.tagged), str(self.tag))

    class Meta:
        ordering = ('tag__name',)
