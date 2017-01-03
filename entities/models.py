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

from django.db import models
from features.memberships import models as memberships


class GestaltContent(models.Model):
    content = models.OneToOneField('content.Content')
    gestalt = models.ForeignKey('gestalten.Gestalt')

    def get_unique_id(self):
        return 'gestalt.{}'.format(self.gestalt.id)


class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('groups.Group')
    pinned = models.BooleanField(default=False)

    def is_external(self):
        return not memberships.Membership.objects.filter(
                group=self.group, member=self.content.author
                ).exists()

    def get_unique_id(self):
        return 'group.{}'.format(self.group.id)
