"""
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

from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import core.models


class ContributionManager(models.Manager):
    def get_by_message_id(self, mid):
        import re
        if mid:
            m = re.match(r'.*\.[0-9]+\.contribution\.([0-9]+)', mid)
            if m:
                return self.get(id=m.group(1))
        raise self.model.DoesNotExist


class Contribution(core.models.Model):
    container = contenttypes.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey('contenttypes.ContentType', related_name='+')

    contribution = contenttypes.GenericForeignKey('contribution_type', 'contribution_id')
    contribution_id = models.PositiveIntegerField()
    contribution_type = models.ForeignKey('contenttypes.ContentType', related_name='+')

    author = models.ForeignKey('gestalten.Gestalt', related_name='contributions')
    in_reply_to = models.ForeignKey('Contribution', null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    objects = ContributionManager()

    class Meta:
        ordering = ('time_created',)

    def get_unique_id(self):
        return '{}.{}.contribution.{}'.format(self.container_type, self.container.id, self.id)


class Text(models.Model):
    text = models.TextField()

    contribution = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='contribution_type',
            object_id_field='contribution_id',
            related_query_name='text')
