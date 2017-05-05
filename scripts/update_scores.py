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

# Update scores (call in a daily cron job)

PROJECT_ROOT = '/home/robert/stadt'
SETTINGS_MODULE = 'stadt.settings'

if __name__ == '__main__':
    sys.path.append(PROJECT_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()

    import core.scores
    import features.gestalten.models
    import features.groups.models
    core.scores.update(features.gestalten.models.Gestalt)
    core.scores.update(features.groups.models.Group)
