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

from features.groups import rules as groups
from features.memberships import rules as memberships
import rules


@rules.predicate
def gestalt_is_member_of(user, group_gestalt):
    group, gestalt = group_gestalt
    return memberships.is_member_of(gestalt.user, group)


@rules.predicate
def has_group(user, group_gestalt):
    group, gestalt = group_gestalt
    return bool(group)


@rules.predicate
def is_closed(user, group_gestalt):
    group, gestalt = group_gestalt
    return groups.is_closed(user, group)


@rules.predicate
def is_member(user, association):
    if association.entity.is_group:
        return memberships.is_member_of(user, association.entity)
    else:
        return user.gestalt == association.entity


@rules.predicate
def is_member_of(user, group_gestalt):
    group, gestalt = group_gestalt
    return memberships.is_member_of(user, group)


@rules.predicate
def is_member_of_any_content_group(user, content):
    for group in content.groups.all():
        if memberships.is_member_of(user, group):
            return True
    return False
