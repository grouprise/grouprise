from . import querysets
from django.contrib.contenttypes import fields as contenttypes
from django.db import models


class Association(models.Model):
    public = models.BooleanField(default=False)
    slug = models.SlugField(default=None, null=True)

    container = contenttypes.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='container_associations')

    entity = contenttypes.GenericForeignKey('entity_type', 'entity_id')
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='entity_associations')

    objects = models.Manager.from_queryset(querysets.Association)()

    class Meta:
        unique_together = ('entity_id', 'entity_type', 'slug')

    def __str__(self):
        return str(self.container)

    def get_absolute_url(self):
        return self.container.get_url_for(self)
