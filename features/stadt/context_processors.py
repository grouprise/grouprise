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

import django.contrib.auth.hashers

from features.associations import models as associations
from features.gestalten import models as gestalten
from features.groups import models as groups


def page_meta(request):
    return {
            'num_groups': groups.Group.objects.count(),
            'num_gestalten': gestalten.Gestalt.objects.exclude(
                user__password__startswith=django.contrib.auth.hashers.
                UNUSABLE_PASSWORD_PREFIX).count(),
            'num_associations': associations.Association.objects.count(),
            }
