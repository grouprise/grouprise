from calendar import LocaleHTMLCalendar, day_abbr, different_locale, month_name
import datetime

from django import urls
from django.utils import timezone


def get_requested_time(request):
    query = request.GET
    month, year = query.get("month", None), query.get("year", None)

    if month and year:
        tz = timezone.get_current_timezone()
        try:
            return datetime.datetime(year=int(year), month=int(month), day=1, tz=tz)
        except ValueError:
            pass
    return None


class EventCalendar(LocaleHTMLCalendar):
    def __init__(self, event_dict, firstweekday=0, locale=None):
        super().__init__(firstweekday, locale)
        self.today = datetime.date.today()
        self.events = event_dict

    def formatday(self, thedate, themonth):
        events = self.events.get(thedate, [])
        url = ""
        if len(events) == 1:
            url = events[0].get_absolute_url()
        elif len(events) > 1:
            url = urls.reverse(
                "day-events", args=["{{:%{}}}".format(c).format(thedate) for c in "Ymd"]
            )
        return {
            "day": thedate.day,
            "events": events,
            "in_month": thedate.month == themonth,
            "today": thedate == self.today,
            "url": url,
        }

    def formatmonthname(self, theyear, themonth):
        with different_locale(self.locale):
            return "%s %s" % (month_name[themonth], theyear)

    def formatmonthweeks(self, theyear, themonth):
        return [
            self.formatweek(week, themonth)
            for week in self.monthdatescalendar(theyear, themonth)
        ]

    def formatweek(self, theweek, themonth):
        return [self.formatday(d, themonth) for d in theweek]

    def formatweekday(self, day):
        with different_locale(self.locale):
            return day_abbr[day]

    def formatweekheader(self):
        return [self.formatweekday(i) for i in self.iterweekdays()]
