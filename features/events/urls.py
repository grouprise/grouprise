from django.conf.urls import url

from features.content import views as content
from . import views

urlpatterns = [
    url(
        r'^stadt/events/$',
        views.List.as_view(),
        name='events'),

    url(
        r'^stadt/events/add/$',
        content.Create.as_view(with_time=True),
        name='create-event'),

    url(
        r'^(?P<entity_slug>[\w-]+)/events/add/$',
        content.Create.as_view(with_time=True),
        name='create-group-event'),

    url(
        r'^(?P<group_slug>[\w-]+)/events/export$',
        views.CalendarExport.as_view(),
        name='group-events-export'),

    url(
        r'^(?P<group_slug>[\w-]+)/events/(?P<domain>public|private).ics$',
        views.CalendarFeed(),
        name='group-events-feed'),
]
