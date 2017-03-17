from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from features.gestalten import models as gestalten


class Content(models.Model):
    title = models.CharField(max_length=255)

    associations = contenttypes.GenericRelation(
            'associations.Association',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='content')

    contributions = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='container_type',
            object_id_field='container_id',
            related_query_name='content')

    def __str__(self):
        return self.title

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(versions__content=self).distinct()


class Version(models.Model):
    content = models.ForeignKey('Content', related_name='versions')

    author = models.ForeignKey('gestalten.Gestalt', related_name='versions')
    text = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
