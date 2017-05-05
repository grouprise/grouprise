"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

import core.models
from core import colors
import django.contrib.contenttypes.models
from django.contrib.contenttypes import fields as contenttypes
from django.core import urlresolvers
from django.db import models


class Group(core.models.Model):
    is_group = True

    date_created = models.DateField(
            auto_now_add=True)
    gestalt_created = models.ForeignKey(
            'gestalten.Gestalt',
            null=True,
            blank=True,
            related_name='+')
    name = models.CharField(
            'Name',
            max_length=255)
    score = models.IntegerField(default=0)
    slug = core.models.AutoSlugField(
            'Adresse der Gruppenseite',
            populate_from='name',
            reserve=['gestalt', 'stadt'],
            unique=True)

    address = models.TextField(
            'Anschrift',
            blank=True)
    avatar = models.ImageField(
            blank=True)
    avatar_color = models.CharField(
            max_length=7,
            default=colors.get_random_color)
    date_founded = models.DateField(
            'Gruppe gegründet',
            null=True,
            blank=True)
    description = models.TextField(
            'Kurzbeschreibung',
            blank=True,
            default='',
            max_length=200)
    logo = models.ImageField(
            blank=True)
    url = models.URLField(
            'Adresse im Web',
            blank=True)

    closed = models.BooleanField(
            'Geschlossene Gruppe',
            default=False,
            help_text='Nur Mitglieder können neue Mitglieder aufnehmen.')

    tags = contenttypes.GenericRelation(
            'tags.Tagged',
            content_type_field='tagged_type',
            object_id_field='tagged_id',
            related_query_name='group')

    associations = django.contrib.contenttypes.fields.GenericRelation(
            'associations.Association', content_type_field='entity_type',
            object_id_field='entity_id', related_query_name='group')

    members = models.ManyToManyField(
            'gestalten.Gestalt', through='memberships.Membership',
            through_fields=('group', 'member'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urlresolvers.reverse(
                'group', args=[type(self).objects.get(pk=self.pk).slug])

    # FIXME: move to template filter
    # TODO: when removed check api
    def get_initials(self):
        import re
        # we prefer initials for all non-trivial terms - but we collect the other initials, as well
        initials = ''
        initials_without_short_terms = ''
        for w in self.name.split():
            m = re.search('[a-zA-Z0-9]', w)
            if not m:
                continue
            initials += m.group(0)
            if w.lower() not in ("der", "die", "das", "des", "dem",
                                 "den", "an", "am", "um", "im", "in"):
                initials_without_short_terms += m.group(0)
        # prefer the non-trivial one - otherwise pick the full one (and hope it is not empty)
        return initials_without_short_terms if initials_without_short_terms else initials

    # FIXME: to be removed
    content = models.ManyToManyField(
            'content.Content',
            related_name='groups',
            through='entities.GroupContent')

    # FIXME: to be removed
    # TODO: when removed check api
    def get_head_gallery(self):
        from features.associations import models as associations
        return associations.Association.objects.filter(
                entity_type=self.content_type, entity_id=self.id,
                content__gallery_images__isnull=False, public=True, pinned=True).first()
