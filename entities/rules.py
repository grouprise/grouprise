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

from features.memberships import rules as memberships_rules
import rules


@rules.predicate
def is_gestalt(user, gestalt):
    return gestalt and user == gestalt.user


@rules.predicate
def is_public(user, gestalt):
    return gestalt.public if gestalt is not None else True


rules.add_perm('entities.view_gestalt', is_public | is_gestalt)
rules.add_perm('entities.change_gestalt', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.create_gestalt_content', rules.is_authenticated & is_gestalt)
rules.add_perm('entities.create_gestalt_message', rules.always_allow)
rules.add_perm('entities.mail_gestalt', rules.is_authenticated & ~is_gestalt)

rules.add_perm(
    'entities.create_group_content', rules.is_authenticated & memberships_rules.is_member_of)

rules.add_perm('entities.view_imprint', rules.always_allow)
