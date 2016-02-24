import calendar as python_calendar
import datetime
from django import template

register = template.Library()

_today = datetime.date.today()


class Calendar(python_calendar.LocaleHTMLCalendar):
    def formatday(self, day, today):
        if day == 0:
            day = '' # day outside month
        return {
                'day': day,
                'today': day == today,
                }

    def formatmonthname(self, theyear=_today.year, themonth=_today.month):
        with python_calendar.different_locale(self.locale):
            return '%s %s' % (python_calendar.month_name[themonth], theyear)

    def formatmonthweeks(self, theyear=_today.year, themonth=_today.month):
        if (theyear, themonth) == (_today.year, _today.month):
            today = _today.day
        else:
            today = 0
        return [self.formatweek(week, today) for week in self.monthdays2calendar(theyear, themonth)]

    def formatweek(self, theweek, today):
        return [self.formatday(d, today) for (d, wd) in theweek]

    def formatweekday(self, day):
        with python_calendar.different_locale(self.locale):
            return python_calendar.day_abbr[day]

    def formatweekheader(self):
        return [self.formatweekday(i) for i in self.iterweekdays()]


@register.inclusion_tag('calendar/_calendar.html')
def calendar():
    c = Calendar()
    return {
            'days': c.formatweekheader(), 
            'month': c.formatmonthname(), 
            'weeks': c.formatmonthweeks(),
            }
