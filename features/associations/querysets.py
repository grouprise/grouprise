from django.contrib.contenttypes import models as contenttypes
from django.db import models
from django.db.models import Max
from features.conversations import models as conversations
from features.groups import models as groups


class Association(models.QuerySet):
    def can_view(self, user, **kwargs):
        if user.is_authenticated():
            group_type = contenttypes.ContentType.objects.get_for_model(groups.Group)
            gestalt_groups = groups.Group.objects.filter(memberships__member=user.gestalt)
            author_query_string = '{}__texts__author'.format(kwargs['container'])
            return self.filter(
                    models.Q(**{author_query_string: user.gestalt})
                    | (models.Q(entity_type=group_type)
                        & models.Q(entity_id__in=gestalt_groups)))
        else:
            return self.none()

    # TODO: replace 'conversation' by generic container
    def ordered_group_conversations(self, user, group):
        qs = self.can_view(user, container='conversation').filter(
            entity_type=contenttypes.ContentType.objects.get_for_model(group),
            entity_id=group.id,
            container_type=contenttypes.ContentType.objects.get_for_model(
                conversations.Conversation))
        qs = qs.annotate(last_activity=Max('conversation__texts__time_created'))
        return qs.order_by('-last_activity')
