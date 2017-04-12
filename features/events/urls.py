from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^stadt/events/$',
        views.List.as_view(),
        name='events'),

    urls.url(r'^(?P<group_slug>[\w-]+)/events/export$',
             views.GroupCalendarExport.as_view(), name='group-events-export'),
    urls.url(r'^(?P<group_slug>[\w-]+)/events/(?P<domain>public|private).ics$',
             views.GroupCalendarFeed(), name='group-events-feed'),
]
