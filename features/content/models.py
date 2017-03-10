from django.contrib.contenttypes import fields as contenttypes
from django.db import models


class Content(models.Model):
    title = models.CharField(max_length=255)

    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='content')

    texts = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='content')

    def __str__(self):
        return self.title
