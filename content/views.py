from . import models
from django.utils import formats
from django.views import generic
from django.views.generic import dates

from utils import views as utils_views


class EventDay(utils_views.PageMixin, generic.DayArchiveView):
    allow_future = True
    context_object_name = 'content_list'
    date_field = 'time'
    menu = 'event'
    model = models.Event
    ordering = 'time'
    parent = 'event-index'
    permission = 'content.view_event_day'

    def get_date(self):
        return dates._date_from_string(
                self.get_year(), self.get_year_format(),
                self.get_month(), self.get_month_format(),
                self.get_day(), self.get_day_format())

    def get_queryset(self):
        if self.get_group():
            return super().get_queryset().filter(groups=self.get_group())
        else:
            return super().get_queryset()

    def get_title(self):
        return formats.date_format(self.get_date())
