import django.urls
from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import grouprise.core
from grouprise.features.gestalten import models as gestalten
from grouprise.features.groups import models as groups


class Conversation(grouprise.core.models.Model):
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

    def get_unique_id(self):
        return self.contributions.first().get_unique_id()

    def get_url_for(self, association):
        return django.urls.reverse('conversation', args=[association.pk])
