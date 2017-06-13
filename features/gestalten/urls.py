from django.conf import urls

import entities.views
from . import views

urlpatterns = [
    urls.url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    urls.url(
        r'^(?P<gestalt_slug>[\w.@+-]+)/$',
        entities.views.Gestalt.as_view(),
        name='gestalt'),

    urls.url(
        # FIXME: remove 'gestalt/' prefix
        r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/events/(?P<domain>public|private).ics$',
        views.CalendarFeed(),
        name='gestalt-events-feed'),
]
