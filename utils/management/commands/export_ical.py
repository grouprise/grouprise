"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

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
