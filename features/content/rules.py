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

from features.associations import models as associations_models, predicates as associations_rules
from features.memberships import rules as memberships
import rules


@rules.predicate
def can_view(user, association):
    return associations_models.Association.objects.can_view(user, container='content') \
            .filter(pk=association.pk).exists()


rules.add_perm(
        'content.list',
        rules.always_allow)

rules.add_perm(
        'content.view',
        can_view)

rules.add_perm(
        'content.comment',
        rules.is_authenticated & can_view)

rules.add_perm(
        'content.create',
        rules.is_authenticated)

rules.add_perm(
        'content.group_create',
        rules.is_authenticated & memberships.is_member_of)

rules.add_perm(
        'content.change',
        rules.is_authenticated & associations_rules.is_member)
