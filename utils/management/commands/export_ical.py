import icalendar

from django.contrib import auth
from django.core.management.base import BaseCommand

from content.models import Event
from entities.models import Gestalt


class Command(BaseCommand):

    help = "Export von Kalender-Daten"

    def add_arguments(self, parser):
        parser.add_argument('--username')

    def handle(self, username=None, **kwargs):
        if username:
            user = auth.get_user_model().objects.get(username=username)
            events = Event.objects.permitted(user)
        else:
            events = Event.objects.public()
        calendar = icalendar.Calendar()
        for event in events:
            cal_event = icalendar.Event()
            cal_event.add("uid", event.id)
            cal_event.add("dtstart", event.time)
            cal_event.add("summary", event.title)
            cal_event.add("description", event.text)
            cal_event.add("location", event.place)
            calendar.add_component(cal_event)
        print(calendar.to_ical().decode("utf-8"))
