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

import calendar as python_calendar
import datetime
import itertools

import django.utils.formats
import django.utils.timezone
from django import template
from django.core import urlresolvers

register = template.Library()


class Calendar(python_calendar.LocaleHTMLCalendar):
    def __init__(self, event_dict, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.today = datetime.date.today()
        self.events = event_dict

    def formatday(self, thedate, themonth):
        events = self.events.get(thedate, [])
        url = ''
        if len(events) == 1:
            url = events[0].get_absolute_url()
        elif len(events) > 1:
            url = urlresolvers.reverse(
                    'event-day', args=['{{:%{}}}'.format(c).format(thedate) for c in 'Ybd'])
        return {
                'day': thedate.day,
                'events': events,
                'in_month': thedate.month == themonth,
                'today': thedate == self.today,
                'url': url,
                }

    def formatmonthname(self, theyear, themonth):
        with python_calendar.different_locale(self.locale):
            return '%s %s' % (python_calendar.month_name[themonth], theyear)

    def formatmonthweeks(self, theyear, themonth):
        return [self.formatweek(week, themonth)
                for week in self.monthdatescalendar(theyear, themonth)]

    def formatweek(self, theweek, themonth):
        return [self.formatday(d, themonth) for d in theweek]

    def formatweekday(self, day):
        with python_calendar.different_locale(self.locale):
            return python_calendar.day_abbr[day]

    def formatweekheader(self):
        return [self.formatweekday(i) for i in self.iterweekdays()]


@register.inclusion_tag('events/_calendar.html')
def calendar(associations, size='preview'):
    around = django.utils.timezone.now()
    # for i in range(add_to_month):
    #     around = around.replace(day=1) + datetime.timedelta(days=32)
    event_associations = associations.filter_events()
    calendar_associations = event_associations.filter(
            content__time__gt=around-datetime.timedelta(weeks=6),
            content__time__lt=around+datetime.timedelta(weeks=6)
            ).order_by('content__time')
    calendar_event_dict = {date: list(events) for date, events in itertools.groupby(
        calendar_associations, key=lambda a: a.container.time.date())}
    calendar = Calendar(calendar_event_dict)
    return {
            'days': calendar.formatweekheader(),
            'month': calendar.formatmonthname(around.year, around.month),
            'weeks': calendar.formatmonthweeks(around.year, around.month),
            'size': size,
            }


@register.filter
def day_preview(associations):
    return ', '.join([
        '{} {}'.format(django.utils.formats.time_format(
            django.utils.timezone.localtime(a.container.time)), a.container.title)
        for a in associations])


@register.inclusion_tag('events/_sidebar_calendar.html')
def sidebar_calendar(associations, group=None, preview_length=5, show_group=True):
    upcoming = associations.filter_upcoming().order_by('content__time')[:preview_length]
    return {
            'associations': associations,
            'group': group,
            'show_group': show_group,
            'upcoming': upcoming,
            }


@register.filter
def upcoming_events(events, preview_length):
    return events.upcoming(preview_length)
