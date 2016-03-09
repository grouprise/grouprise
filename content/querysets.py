import datetime
from django.db import models
from django.utils import timezone


class EventQuerySet(models.QuerySet):
    def around(self, time):
        delta = datetime.timedelta(weeks=6)
        return self.filter(time__gt=time-delta, time__lt=time+delta)

    def upcoming(self, count):
        return self.filter(time__gte=timezone.now())[:count]
