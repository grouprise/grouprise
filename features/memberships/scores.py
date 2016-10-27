import datetime
from django.conf import settings
from django.utils import timezone


class Group:
    THRESHOLD = timezone.now() - datetime.timedelta(days=settings.SCORE_CONTENT_AGE)
    
    @classmethod
    def get_num_gestalten(cls, group):
        return group.memberships.count()

    @classmethod
    def get_queryset(cls, group):
        return group.groupcontent_set.filter(content__date_created__gt=cls.THRESHOLD)

    @classmethod
    def score(cls, instance):
        s = 0
        for a in cls.get_queryset(instance):
            s += settings.SCORE_CONTENT_AGE - (timezone.now() - a.content.date_created).days
        return s * cls.get_num_gestalten(instance)
