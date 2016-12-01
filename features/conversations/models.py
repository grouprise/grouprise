from django.contrib.contenttypes import fields as contenttypes
from django.db import models


class Conversation(models.Model):
    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')
    subject = models.CharField('Thema', max_length=255)
    texts = contenttypes.GenericRelation(
            'texts.Text',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    def __str__(self):
        return self.subject
