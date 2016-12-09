from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from entities import models as gestalten


class Conversation(models.Model):
    subject = models.CharField(max_length=255)

    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    texts = contenttypes.GenericRelation(
            'texts.Text',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    def __str__(self):
        return self.subject

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(texts__conversation=self).distinct()
