import datetime
from django.db import models


class EventQuerySet(models.QuerySet):
    def around(self, time):
        delta = datetime.timedelta(weeks=6)
        now = datetime.datetime.now()
        return self.filter(time__gt=now-delta, time__lt=now+delta)

    def upcoming(self, count):
        return self.filter(time__gte=datetime.datetime.now())[:count]
