#!/usr/bin/env python
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

import django
import os
import sys

# Mass subscribe emails in FILENAME to group with GROUP_SLUG

PROJECT_ROOT = '/srv/stadtgestalten'
SETTINGS_MODULE = 'stadt.settings'
FILENAME = '/home/user/mails.txt'
GROUP_SLUG = 'group-slug'

if __name__ == '__main__':
    sys.path.append(PROJECT_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()

    emails = []
    with open(FILENAME) as f:
        emails = f.readlines()

    for email in [e.strip() for e in emails]:
        if email:
            from django.db.utils import IntegrityError
            from entities.models import Gestalt
            from features.groups.models import Group
            from features.subscriptions.models import Subscription
            gestalt = Gestalt.get_or_create(email)
            group = Group.objects.get(slug=GROUP_SLUG)
            try:
                Subscription.objects.create(
                        subscribed_to=group, subscriber=gestalt)
            except IntegrityError:
                pass
