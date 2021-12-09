from django.urls import path, re_path

from grouprise.features.events.views import (
    Attendance,
    Create,
    Day,
    GroupCalendarExport,
    GroupCalendarFeed,
    List,
    SiteCalendarExport,
    SiteCalendarFeed,
)

urlpatterns = [
    path("stadt/events", List.as_view(), name="events"),
    path("stadt/events/add", Create.as_view(), name="create-event"),
    path(
        "stadt/events/export", SiteCalendarExport.as_view(), name="export-site-events"
    ),
    path("stadt/events/public.ics", SiteCalendarFeed(), name="site-events-feed"),
    path(
        "stadt/events/<int:year>/<int:month>/<int:day>",
        Day.as_view(),
        name="day-events",
    ),
    path("<slug:entity_slug>/events/add", Create.as_view(), name="create-group-event"),
    path(
        "<slug:group_slug>/events/export",
        GroupCalendarExport.as_view(),
        name="group-events-export",
    ),
    path(
        "stadt/content/<int:association_pk>/events/attendees",
        Attendance.as_view(),
        name="group-event-attendance",
    ),
    re_path(
        r"(?P<group_slug>[\w-]+)/events/(?P<domain>public|private).ics",
        GroupCalendarFeed(),
        name="group-events-feed",
    ),
]
