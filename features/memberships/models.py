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


class Membership(models.Model):
    created_by = models.ForeignKey(
            'gestalten.Gestalt', related_name='memberships_created')
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('groups.Group', related_name='memberships')
    member = models.ForeignKey('gestalten.Gestalt', related_name='memberships')

    def __str__(self):
        return "%s is member of %s since %s" % (
            str(self.member.user.get_username()),
            str(self.group.slug), str(self.date_joined)
        )

    class Meta:
        unique_together = ('group', 'member')
