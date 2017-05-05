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

from django.core import cache
from django.core.cache.backends import base


class ProxyCache(base.BaseCache):
    def __init__(self, location, params):
        super().__init__(params)
        self.cache = cache.caches['proxy']

    def get(self, key, default=None, version=None):
        return self.cache.get(key, default=default, version=version)

    def set(self, key, value, timeout=None, version=None):
        return self.cache.set(key, value, timeout=timeout, version=version)

    def delete(self, key):
        return self.cache.delete(key)

    def clear(self):
        return self.cache.clear()
