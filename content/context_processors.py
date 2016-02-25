from . import models
import datetime
from django.conf import settings


def events(request):
    return {
            'calendar_events': models.Event.objects.around(datetime.datetime.now()),
            'upcoming_events': models.Event.objects.upcoming(settings.UPCOMING_EVENTS_PREVIEW_COUNT),
            }


def statistics(request):
    return {
            'content_count': models.Content.objects.count,
            }
