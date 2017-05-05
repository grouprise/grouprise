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

from core import fragments

fragments.register(
        'group-meta-subscriptions-share', 'sharing/_group_meta_share.html')
fragments.register('invite-member', 'sharing/_invite_member.html')
fragments.register('sidebar-share-group', 'sharing/_sidebar_group.html')

fragments.insert(
        'group-meta-subscriptions-share',
        'group-meta-subscriptions')

fragments.insert(
        'invite-member',
        'group-meta-members')

fragments.insert(
        'sidebar-share-group',
        'group-sidebar',
        after=['sidebar-logo', 'sidebar-calendar'],
        before=['sidebar-groups'])
