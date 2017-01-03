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

from . import models, test_memberships as memberships, test_mixins as mixins
from core import tests
from features.gestalten import tests as gestalten
from features.groups import models as groups_models, tests as groups


class CreatedGroupHasNoMembers:
    def test_members(self):
        self.client.post(self.get_url('group-create'), {'name': 'Test'})
        group = groups_models.Group.objects.get(name='Test')
        self.assertNotExists(models.Membership, group=group)


class CreatedGroupHasGestaltMember:
    def test_members(self):
        self.client.post(self.get_url('group-create'), {'name': 'Test'})
        group = groups_models.Group.objects.get(name='Test')
        self.assertExists(models.Membership, group=group, member=self.gestalt)


class GroupAnonymous(
        memberships.OnlyJoinLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        groups.GroupMixin, tests.Test):
    pass


class GroupAuthenticated(
        memberships.OnlyJoinLink,
        memberships.JoinAllowed,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        gestalten.AuthenticatedMixin, groups.GroupMixin, tests.Test):
    pass


class GroupClosed(
        memberships.NoLink,
        memberships.JoinForbidden,
        memberships.ResignForbidden,
        memberships.MemberListForbidden,
        memberships.MemberCreateForbidden,
        gestalten.AuthenticatedMixin, groups.ClosedGroupMixin, tests.Test):
    pass


class GroupMember(
        memberships.OnlyResignLink,
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        memberships.MemberListNoCreateLink,
        memberships.MemberCreateForbidden,
        mixins.AuthenticatedMemberMixin, gestalten.OtherGestaltMixin, tests.Test):
    pass


class GroupClosedMember(
        memberships.OnlyResignLink,
        memberships.JoinForbidden,
        memberships.ResignAllowed,
        memberships.MemberListCreateLink,
        memberships.MemberCreateAllowedWithEmail,
        memberships.MemberCreateSendsNotification,
        mixins.AuthenticatedMemberMixin, groups.ClosedGroupMixin,
        gestalten.OtherGestaltMixin, tests.Test):
    pass


class AnonymousUserCreatesGroup(
        CreatedGroupHasNoMembers,
        tests.Test):
    """
    If an anonymous user creates a group:
    * it has no members
    """


class GestaltCreatesGroup(
        CreatedGroupHasGestaltMember,
        gestalten.AuthenticatedMixin, tests.Test):
    """
    If a gestalt wants to create a group:
    * it has the gestalt as a member
    """
