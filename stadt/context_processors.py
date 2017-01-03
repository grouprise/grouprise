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

from django.contrib.sites import shortcuts
from django.conf import settings


def site(request):
    return {
        'http_origin': request.build_absolute_uri("/").rstrip("/"),
        'site': shortcuts.get_current_site(request),

        'site_description':
        'Stadtgestalten ist eine neue Internet-Plattform und ermöglicht '
        'aktiven, engagierten Menschen und Gruppen in der Stadt, sich '
        'unkompliziert zu informieren, zu präsentieren und miteinander zu '
        'vernetzen.',
    }


def assets(request):
    return {'asset_version': settings.ASSET_VERSION}
