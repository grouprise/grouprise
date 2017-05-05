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

from django.conf import settings, urls
from django.conf.urls import static
from django.contrib import admin

urlpatterns = [
    urls.url(r'^stadt/admin/', admin.site.urls),
    urls.url(r'^stadt/api/', urls.include('core.api_urls')),

    urls.url(r'^stadt/', urls.include('account.urls')),
    urls.url(r'^stadt/', urls.include('content.urls')),
    urls.url(r'^stadt/', urls.include('entities.urls')),
    urls.url(r'^stadt/', urls.include('features.associations.urls')),
    urls.url(r'^stadt/', urls.include('features.conversations.urls')),
    urls.url(r'^stadt/', urls.include('features.memberships.urls')),
    urls.url(r'^stadt/', urls.include('features.sharing.urls')),
    urls.url(r'^stadt/', urls.include('features.subscriptions.urls')),
    urls.url(r'^stadt/', urls.include('features.tags.urls')),

    urls.url(r'^', urls.include('features.articles.urls')),
    urls.url(r'^', urls.include('features.events.urls')),
    urls.url(r'^', urls.include('features.galleries.urls')),
    urls.url(r'^', urls.include('features.stadt.urls')),

    # matches /*/, should be included late, groups before gestalten
    urls.url(r'^', urls.include('features.groups.urls')),
    urls.url(r'^', urls.include('features.gestalten.urls')),

    # matches /*/*/, should be included at last
    urls.url(r'^', urls.include('features.content.urls')),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
