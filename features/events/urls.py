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

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/events/$',
        views.List.as_view(),
        name='events'),

    url(
        r'^stadt/events/add/$',
        views.Create.as_view(),
        name='create-event'),

    url(
        r'^(?P<entity_slug>[\w-]+)/events/add/$',
        views.Create.as_view(),
        name='create-group-event'),

    url(
        r'^(?P<group_slug>[\w-]+)/events/export$',
        views.GroupCalendarExport.as_view(),
        name='group-events-export'),

    url(
        r'^(?P<group_slug>[\w-]+)/events/(?P<domain>public|private).ics$',
        views.GroupCalendarFeed(),
        name='group-events-feed'),
]
