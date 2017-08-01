import django.utils.timezone
from django.contrib.contenttypes import models as contenttypes
from django.db import models
from django.db.models import Max, Min

from features.content import models as content
from features.conversations import models as conversations
from features.gestalten import models as gestalten
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

    def filter_articles(self):
        qs = self
        qs = qs.filter(content__time__isnull=True)  # events
        qs = qs.filter(content__gallery_images__image__isnull=True)  # galleries
        return qs

    def filter_events(self):
        return self.filter(content__time__isnull=False)

    def filter_group_containers(self):
        return self.filter(entity_type=groups.Group.content_type)

    def filter_upcoming(self, time=None):
        return self.filter(content__time__gte=time or django.utils.timezone.now())

    def filter_user_content(self, user):
        qs = self
        qs = qs.can_view(user)
        qs = qs.filter(container_type=content.Content.content_type)
        return qs

    def ordered_user_content(self, user):
        qs = self
        qs = qs.filter_user_content(user)
        qs = qs.annotate(time_created=Min('content__versions__time_created'))
        qs = qs.order_by('-time_created')
        return qs

    def ordered_user_conversations(self, user):
        qs = self
        qs = qs.can_view(user, container='conversation')
        qs = qs.filter(container_type=conversations.Conversation.content_type)
        qs = qs.annotate(last_activity=Max('conversation__contributions__time_created'))
        qs = qs.order_by('-last_activity')
        return qs
