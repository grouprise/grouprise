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
from features.groups import rules as groups
import rules
import rules.permissions


@rules.predicate
def is_member(user, membership):
    if membership:
        return membership.member == user.gestalt
    return False


@rules.predicate
def is_member_of(user, group):
    try:
        return models.Membership.objects.filter(
                group=group,
                member=user.gestalt
                ).exists()
    except AttributeError:
        return None


rules.add_perm(
        'memberships.join_group',
        rules.is_authenticated
        & ~is_member_of
        & ~groups.is_closed)

rules.add_perm(
        'memberships.create_membership',
        rules.is_authenticated
        & groups.is_closed
        & is_member_of)

rules.add_perm(
        'memberships.delete_membership',
        rules.is_authenticated
        & is_member)

rules.add_perm(
        'memberships.view_list',
        rules.is_authenticated
        & is_member_of)


# redefinition of groups permissions

if rules.perm_exists('groups.change_group'):
    rules.remove_perm('groups.change_group')

rules.add_perm(
        'groups.change_group',
        rules.is_authenticated
        & is_member_of)
