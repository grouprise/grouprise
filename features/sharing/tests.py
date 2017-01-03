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

from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class GroupRecommend(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def test_group_recommend(self):
        self.client.post(
                self.get_url('group-recommend', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)


class MemberInvite(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def test_member_invite(self):
        self.client.post(
                self.get_url('member-invite', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)
