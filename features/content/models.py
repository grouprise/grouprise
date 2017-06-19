import django.contrib.contenttypes.models
import django.core.urlresolvers
from django.contrib.contenttypes import fields as contenttypes
from django.db import models
from django.db.models import Q

import core.models
from features.gestalten import models as gestalten
from features.groups import models as groups


class Content(core.models.Model):
    is_conversation = False

    title = models.CharField(max_length=255)
    image = models.ForeignKey('images.Image', null=True)

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

    def __str__(self):
        return self.title

    def get_authors(self):
        return gestalten.Gestalt.objects.filter(
                Q(versions__content=self) | Q(contributions__content=self)).distinct()

    def get_associated_gestalten(self):
        return gestalten.Gestalt.objects.filter(associations__content=self)

    def get_associated_groups(self):
        return groups.Group.objects.filter(associations__content=self)

    def get_unique_id(self):
        return 'content.{}'.format(self.id)

    def get_url_for(self, association):
        return django.core.urlresolvers.reverse(
                'content', args=[association.entity.slug, association.slug])

    @property
    def is_event(self):
        return self.time is not None

    @property
    def is_gallery(self):
        return self.gallery_images.count() > 0

    @property
    def subject(self):
        return self.title


class Version(models.Model):
    content = models.ForeignKey('Content', related_name='versions')

    author = models.ForeignKey('gestalten.Gestalt', related_name='versions')
    text = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
