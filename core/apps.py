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

from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.utils import module_loading
        module_loading.import_string(
                settings.ROOT_SIGNALCONF + '.connections')
        module_loading.autodiscover_modules('fragments')
        module_loading.autodiscover_modules('rest_api')
        module_loading.autodiscover_modules('markdown')
        module_loading.autodiscover_modules('signals')
