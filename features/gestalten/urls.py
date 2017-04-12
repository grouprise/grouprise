from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^gestalt/(?P<gestalt_slug>[\w.@+-]+)/events/(?P<domain>public|private).ics$',
             views.CalendarFeed(), name='gestalt-events-feed'),
    urls.url(r'^gestalten/$',
             views.List.as_view(),
             name='gestalten'),
]
