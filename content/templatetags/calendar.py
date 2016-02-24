import calendar as python_calendar
import datetime
from django import template
from django.utils import safestring


register = template.Library()


@register.simple_tag
def calendar():
    today = datetime.date.today()
    return safestring.mark_safe(python_calendar.LocaleHTMLCalendar().formatmonth(today.year, today.month))
