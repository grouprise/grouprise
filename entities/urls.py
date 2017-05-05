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

from . import views
from django.conf import urls


urlpatterns = [
    # gestalten
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/$',
        views.GestaltUpdate.as_view(),
        name='gestalt-update'),
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GestaltAvatarUpdate.as_view(),
        name='gestalt-avatar-update'),
    urls.url(
        r'^gestalt/(?P<pk>[0-9]+)/edit/background/$',
        views.GestaltBackgroundUpdate.as_view(),
        name='gestalt-background-update'),

    # groups
    urls.url(
        r'^group/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GroupAvatarUpdate.as_view(),
        name='group-avatar-update'),
    urls.url(
        r'^group/(?P<pk>[0-9]+)/edit/logo/$',
        views.GroupLogoUpdate.as_view(),
        name='group-logo-update'),


    urls.url(r'^imprint/$', views.Imprint.as_view(), name='imprint'),
    urls.url(r'^privacy/$', views.Privacy.as_view(), name='privacy'),
]
