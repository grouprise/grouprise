import calendar as python_calendar
import datetime
import itertools

import django.utils.timezone
from django import template
from django.core import urlresolvers

from content import models as content

register = template.Library()


class Calendar(python_calendar.LocaleHTMLCalendar):
    def __init__(self, events, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.today = datetime.date.today()
        self.events = {}
        for date, events in itertools.groupby(events, key=lambda e: e.date()):
            self.events[date] = list(events)

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


@register.inclusion_tag('events/_calendar.html', takes_context=True)
def calendar(context, user, events=None, add_to_month=0, size='preview'):
    around = django.utils.timezone.now()
    for i in range(add_to_month):
        around = around.replace(day=1) + datetime.timedelta(days=32)
    if events is None:
        events = content.Event.objects.can_view(user).around(around)
    c = Calendar(events)
    return {
            'size': size,
            'days': c.formatweekheader(),
            'group': context.get('group'),
            'month': c.formatmonthname(around.year, around.month),
            'weeks': c.formatmonthweeks(around.year, around.month),
            }


@register.inclusion_tag('events/_sidebar_calendar.html')
def sidebar_calendar(user=None, events=None, preview_length=5, show_group=True, group=None):
    if events is None:
        events = content.Event.objects.can_view(user)
    return {
            'events': events,
            'group': group,
            'preview_length': preview_length,
            'show_group': show_group,
            }


@register.filter
def upcoming_events(events, preview_length):
    return events.upcoming(preview_length)
