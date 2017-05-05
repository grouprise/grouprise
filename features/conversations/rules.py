"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

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

from entities import rules as gestalten
from features.associations import models as associations
from features.memberships import rules as memberships
import rules


@rules.predicate
def can_view(user, association):
    return associations.Association.objects.can_view(user, container='conversation') \
            .filter(pk=association.pk).exists()


rules.add_perm(
        'conversations.create_gestalt_conversation',
        rules.is_authenticated
        | gestalten.is_public
        )

rules.add_perm(
        'conversations.create_group_conversation',
        rules.always_allow)

rules.add_perm(
        'conversations.list',
        rules.always_allow)

rules.add_perm(
        'conversations.list_group',
        memberships.is_member_of)

rules.add_perm(
        'conversations.reply',
        can_view)

rules.add_perm(
        'conversations.view',
        can_view)
