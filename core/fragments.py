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

fragments = {}
groups = {}


def register(key, fragment):
    fragments[key] = fragment


def always():
    return True


def insert(key, group_name, predicate=always, after=[], before=[]):
    group = groups.get(group_name, [])
    min_index = 0
    for item in after:
        try:
            min_index = max(min_index, group.index(item)+1)
        except ValueError:
            pass
    max_index = len(group)
    for item in before:
        try:
            max_index = min(max_index, group.index(item))
        except ValueError:
            pass
    if min_index <= max_index:
        group.insert(max_index, key)
        groups[group_name] = group


def register2(fragment, group, before=[]):
    key = '{}-{}'.format(group, fragment)
    register(key, fragment)
    b = []
    for k in before:
        b.append('{}-{}'.format(group, k))
    insert(key, group, before=b)
