from . import models
from django.conf import settings
from django.utils import timezone

def events(request):
    return {
            'calendar_events': models.Event.objects.around(timezone.now()),
            'upcoming_events': models.Event.objects.upcoming(settings.UPCOMING_EVENTS_PREVIEW_COUNT),
            }

def statistics(request):
    return {
            'content_count': models.Content.objects.permitted(request.user).count,
            }
