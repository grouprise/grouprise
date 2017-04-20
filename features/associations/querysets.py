import django.utils.timezone
from django.contrib.contenttypes import models as contenttypes
from django.db import models
from django.db.models import Max

from features.gestalten import models as gestalten
from features.conversations import models as conversations
from features.groups import models as groups


class Association(models.QuerySet):
    def can_view(self, user, container=None):
        # public associations can be viewed
        query = models.Q(public=True)
        # authenticated users can view associations for entities they are members in
        if user.is_authenticated():
            GESTALT_TYPE = contenttypes.ContentType.objects.get_for_model(gestalten.Gestalt)
            GROUP_TYPE = contenttypes.ContentType.objects.get_for_model(groups.Group)
            gestalt_groups = groups.Group.objects.filter(memberships__member=user.gestalt)
            query |= (
                    (models.Q(entity_type=GROUP_TYPE)
                        & models.Q(entity_id__in=gestalt_groups))
                    | (models.Q(entity_type=GESTALT_TYPE)
                        & models.Q(entity_id=user.gestalt.id))
                    )
            # if given a container we can allow access to associations for which the user
            # authored a contribution (e.g. for container='conversation')
            if container:
                author_query_string = '{}__contributions__author'.format(container)
                query |= models.Q(**{author_query_string: user.gestalt})
        return self.filter(query)

    def filter_events(self):
        return self.filter(content__time__isnull=False)

    def filter_upcoming(self):
        return self.filter(content__until_time__gt=django.utils.timezone.now())

    # TODO: replace 'conversation' by generic container
    def ordered_conversations(self, user):
        qs = self.can_view(user, container='conversation').filter(
            container_type=contenttypes.ContentType.objects.get_for_model(
                conversations.Conversation))
        qs = qs.annotate(last_activity=Max('conversation__contributions__time_created'))
        return qs.order_by('-last_activity')
