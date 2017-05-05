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

import django.core.urlresolvers
from django.contrib.contenttypes import fields as contenttypes
from django.db import models

from features.gestalten import models as gestalten
from features.groups import models as groups


class Conversation(models.Model):
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
