import datetime
from django.conf import settings
from django.contrib.contenttypes import models as contenttypes
from django.utils import timezone
from features.associations import models as associations
from features.conversations import models as conversations
from features.groups import models as groups


class Group:
    THRESHOLD = timezone.now() - datetime.timedelta(days=settings.SCORE_CONTENT_AGE)

    @classmethod
    def get_associations(cls, group):
        return associations.Association.objects.filter(
                entity_type=contenttypes.ContentType.objects.get_for_model(group),
                entity_id=group.id,
                container_type=contenttypes.ContentType.objects.get_for_model(
                    conversations.Conversation),
                conversation__texts__time_created__gt=cls.THRESHOLD
                ).distinct()

    @classmethod
    def get_num_gestalten(cls, group):
        return group.memberships.count()

    @classmethod
    def get_groupcontent(cls, group):
        return group.groupcontent_set.filter(content__date_created__gt=cls.THRESHOLD)

    @classmethod
    def score(cls, instance):
        if isinstance(instance, groups.Group):
            s = 0
            for a in cls.get_groupcontent(instance):
                s += settings.SCORE_CONTENT_AGE - (timezone.now() - a.content.date_created).days
            for a in cls.get_associations(instance):
                s += settings.SCORE_CONTENT_AGE - (
                        timezone.now() - a.container.texts.last().time_created).days
            return s * cls.get_num_gestalten(instance)
        return 0
