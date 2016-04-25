import datetime
from django.db import models
from django.utils import timezone
from entities import models as entities_models


class ContentQuerySet(models.QuerySet):
    def permitted(self, user):
        if user.is_authenticated():
            return self.filter(
                    models.Q(public=True) |
                    models.Q(author=user.gestalt) |
                    models.Q(groupcontent__group__in=user.gestalt.groups.all()) |
                    models.Q(gestaltcontent__gestalt=user.gestalt)
                    )
        else:
            return self.public()

    def public(self):
        return self.filter(public=True)


class EventQuerySet(ContentQuerySet):
    def around(self, time):
        delta = datetime.timedelta(weeks=6)
        return self.filter(time__gt=time-delta, time__lt=time+delta)

    def upcoming(self, count=None):
        return self.filter(time__gte=timezone.now())[:count]
