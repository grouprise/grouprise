from . import models
import datetime
from django.conf import settings


def events(request):
    calendar_events = models.Event.objects.around(datetime.datetime.now())
    calendar_dates = map(lambda t: t.date(), calendar_events.values_list('time', flat=True))
    upcoming_events = models.Event.objects.upcoming(settings.UPCOMING_EVENTS_PREVIEW_COUNT)
    return {
            'calendar_events': dict(zip(calendar_dates, calendar_events)),
            'upcoming_events': upcoming_events,
            }


def statistics(request):
    return {'content_count': models.Content.objects.count}
