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

from . import models
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class MemberMixin(gestalten.GestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.gestalt, group=cls.group, member=cls.gestalt)


class OtherMemberMixin(gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.other_gestalt,
                group=cls.group,
                member=cls.other_gestalt)


class AuthenticatedMemberMixin(MemberMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.gestalt.user)


class OtherAuthenticatedMemberMixin(OtherMemberMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.other_gestalt.user)
