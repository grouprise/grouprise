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

from django.conf import settings
from django.utils import module_loading


def get_score_processors():
    return [module_loading.import_string(s) for s in settings.SCORE_PROCESSORS]


def update(model):
    for instance in model._default_manager.all():
        instance.score = 0
        for p in get_score_processors():
            instance.score += p.score(instance)
        instance.save()
