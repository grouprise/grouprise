import icalendar

from django.contrib import auth
from django.core.management.base import BaseCommand
import django.contrib.sites.models

from content.models import Event


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
        uid_format = "{}@" + django.contrib.sites.models.Site.objects.get_current().domain
        for event in events:
            cal_event = icalendar.Event()
            # jede UID sollte global eindeutig sein - also inkl. Domain
            cal_event.add("uid", uid_format.format(event.id))
            cal_event.add("dtstart", event.time)
            cal_event.add("summary", event.title)
            cal_event.add("description", event.text)
            cal_event.add("location", event.place)
            calendar.add_component(cal_event)
        print(calendar.to_ical().decode("utf-8"))
