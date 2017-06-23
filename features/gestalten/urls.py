from django.conf import urls

from . import views

urlpatterns = [
    urls.url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    urls.url(
        # TODO: remove 'gestalt/' prefix
        r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/events/(?P<domain>public|private).ics$',
        views.CalendarFeed(),
        name='gestalt-events-feed'),

    urls.url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/$',
        views.GestaltUpdate.as_view(),
        name='gestalt-update'),

    urls.url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/avatar/$',
        views.GestaltAvatarUpdate.as_view(),
        name='gestalt-avatar-update'),

    urls.url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/background/$',
        views.GestaltBackgroundUpdate.as_view(),
        name='gestalt-background-update'),
]
