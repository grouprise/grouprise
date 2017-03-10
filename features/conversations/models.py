from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from features.gestalten import models as gestalten
from features.groups import models as groups


class Conversation(models.Model):
    subject = models.CharField(max_length=255)

    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    texts = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='conversation')

    def __str__(self):
        return self.subject

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(texts__conversation=self).distinct()

    def get_gestalten(self):
        gestalt_associations = self.associations.filter(
                entity_type=contenttypes.ContentType.objects.get_for_model(gestalten.Gestalt))
        return gestalten.Gestalt.objects.filter(
                pk__in=gestalt_associations.values_list('entity_id', flat=True))

    def get_groups(self):
        group_associations = self.associations.filter(
                entity_type=contenttypes.ContentType.objects.get_for_model(groups.Group))
        return groups.Group.objects.filter(
                pk__in=group_associations.values_list('entity_id', flat=True))
