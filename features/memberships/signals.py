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

from . import models, notifications
from core import signals
from features.groups import models as groups


def add_first_member(group):
    if group.gestalt_created:
        models.Membership.objects.create(
                created_by=group.gestalt_created,
                group=group, member=group.gestalt_created)


def creator_is_not_member(membership):
    return membership.created_by != membership.member


connections = [
    signals.connect_action(
        signals.model_created, add_first_member,
        senders=[groups.Group],
        ),
    signals.connect_notification(
        signals.model_created, notifications.MembershipCreated,
        instance='membership',
        predicate=creator_is_not_member,
        senders=[models.Membership],
        ),
    ]
