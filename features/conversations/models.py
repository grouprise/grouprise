import django.urls
from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import core
from features.gestalten import models as gestalten
from features.groups import models as groups


class Conversation(core.models.Model):
    is_conversation = True

    subject = models.CharField(max_length=255)

    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    contributions = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    @classmethod
    def get_content_type(cls):
        return django.contrib.contenttypes.models.ContentType.objects.get_for_model(cls)

    def __str__(self):
        return self.subject

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(contributions__conversation=self).distinct()

    def get_associated_gestalten(self):
        return gestalten.Gestalt.objects.filter(associations__conversation=self)

    def get_associated_groups(self):
        return groups.Group.objects.filter(associations__conversation=self)

    def get_url_for(self, association):
        return django.core.urlresolvers.reverse('conversation', args=[association.pk])
