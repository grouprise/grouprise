import django.contrib.contenttypes.models
import django.core.urlresolvers
from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from features.gestalten import models as gestalten


class Content(models.Model):
    title = models.CharField(max_length=255)

    place = models.CharField(blank=True, max_length=255)

    time = models.DateTimeField(blank=True, null=True)
    until_time = models.DateTimeField(blank=True, null=True)
    all_day = models.BooleanField(default=False)

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

    @classmethod
    def get_content_type(cls):
        return django.contrib.contenttypes.models.ContentType.objects.get_for_model(cls)

    def __str__(self):
        return self.title

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(versions__content=self).distinct()

    def get_url_for(self, association):
        return django.core.urlresolvers.reverse(
                'content', args=[association.entity.slug, association.slug])


class Version(models.Model):
    content = models.ForeignKey('Content', related_name='versions')

    author = models.ForeignKey('gestalten.Gestalt', related_name='versions')
    text = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
