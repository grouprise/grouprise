import calendar as python_calendar
import datetime
from django import template

register = template.Library()

_today = datetime.date.today()


class Calendar(python_calendar.LocaleHTMLCalendar):
    def __init__(self, events, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.events = events

    def formatday(self, thedate, themonth):
        return {
                'day': thedate.day,
                'event': self.events.get(thedate),
                'in_month': thedate.month == themonth,
                'today': thedate == _today,
                }

    def formatmonthname(self, theyear=_today.year, themonth=_today.month):
        with python_calendar.different_locale(self.locale):
            return '%s %s' % (python_calendar.month_name[themonth], theyear)

    def formatmonthweeks(self, theyear=_today.year, themonth=_today.month):
        return [self.formatweek(week, themonth) for week in self.monthdatescalendar(theyear, themonth)]

    def formatweek(self, theweek, themonth):
        return [self.formatday(d, themonth) for d in theweek]

    def formatweekday(self, day):
        with python_calendar.different_locale(self.locale):
            return python_calendar.day_abbr[day]

    def formatweekheader(self):
        return [self.formatweekday(i) for i in self.iterweekdays()]


@register.inclusion_tag('calendar/_calendar.html')
def calendar(events):
    c = Calendar(events)
    return {
            'days': c.formatweekheader(), 
            'month': c.formatmonthname(), 
            'weeks': c.formatmonthweeks(),
            }
