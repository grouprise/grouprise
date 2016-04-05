import datetime
from django.db import models
from django.utils import timezone
from entities import models as entities_models

class ContentQuerySet(models.QuerySet):
    def permitted(self, user):
        gestalt = user.gestalt if user.is_authenticated() else None
        user_groups = user.gestalt.group_set.all() if user.is_authenticated() else entities_models.Group.objects.none()
        return self.filter(models.Q(public=True) | models.Q(author=gestalt) | models.Q(groupcontent__group__in=user_groups) | models.Q(gestaltcontent__gestalt=gestalt))

class EventQuerySet(models.QuerySet):
    def around(self, time):
        delta = datetime.timedelta(weeks=6)
        return self.filter(time__gt=time-delta, time__lt=time+delta)

    def upcoming(self, count):
        return self.filter(time__gte=timezone.now())[:count]
