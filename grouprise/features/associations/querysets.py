import django.utils.timezone
from django.contrib.contenttypes import models as contenttypes
from django.db import models
from django.db.models import Max, Min, Q
from django.db.models.functions import Coalesce, Greatest

from grouprise.features.content import models as content
from grouprise.features.conversations import models as conversations
from grouprise.features.gestalten import models as gestalten
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups import models as groups
from grouprise.features.groups.models import Group


class Association(models.QuerySet):
    def can_view(self, user, container=None):
        # public associations can be viewed
        query = models.Q(public=True)
        # authenticated users can view associations for entities they are members in
        if user.is_authenticated:
            gestalt_type = contenttypes.ContentType.objects.get_for_model(gestalten.Gestalt)
            group_type = contenttypes.ContentType.objects.get_for_model(groups.Group)
            gestalt_groups = groups.Group.objects.filter(memberships__member=user.gestalt)
            query |= (
                    (models.Q(entity_type=group_type)
                        & models.Q(entity_id__in=gestalt_groups))
                    | (models.Q(entity_type=gestalt_type)
                        & models.Q(entity_id=user.gestalt.id))
                    )
            # if given a container we can allow access to associations for which the user
            # authored a contribution (e.g. for container='conversation')
            if container:
                author_query_string = '{}__contributions__author'.format(container)
                query |= models.Q(**{author_query_string: user.gestalt})
        return self.exclude_deleted().filter(query)

    def exclude_deleted(self):
        return self.exclude(deleted__isnull=False)

    def filter_articles(self):
        qs = self
        qs = qs.filter(content__time__isnull=True)  # events
        qs = qs.filter(content__gallery_images__image__isnull=True)  # galleries
        qs = qs.filter(content__poll__isnull=True)  # polls
        qs = qs.filter(content__versions__file__isnull=True)  # files
        return qs

    def filter_events(self):
        return self.filter(content__time__isnull=False)

    def filter_galleries(self):
        return self.filter(content__gallery_images__image__isnull=False)

    def filter_group_containers(self):
        return self.filter(entity_type=groups.Group.content_type)

    def filter_upcoming(self, time=None):
        return self.filter(content__time__gte=time or django.utils.timezone.now())

    def filter_user_content(self, user):
        qs = self
        qs = qs.can_view(user)
        qs = qs.filter(container_type=content.Content.content_type)
        return qs

    def order_content_by_time_created(self, ascending=True):
        qs = self
        qs = qs.annotate(time_created=Min('content__versions__time_created'))
        qs = qs.order_by('time_created' if ascending else '-time_created')
        return qs

    def ordered_user_content(self, user):
        qs = self
        qs = qs.filter_user_content(user)
        qs = qs.order_content_by_time_created(ascending=False)
        return qs

    def ordered_user_conversations(self, user):
        qs = self
        qs = qs.can_view(user, container='conversation')
        qs = qs.filter(container_type=conversations.Conversation.content_type)
        qs = qs.annotate(last_activity=Max('conversation__contributions__time_created'))
        qs = qs.order_by('-last_activity')
        return qs

    def ordered_user_associations(self, user):
        qs = self
        qs = qs.exclude(
                Q(public=True) & (
                    Q(entity_type=Gestalt.content_type)
                    | (Q(entity_type=Group.content_type)
                        & ~Q(entity_id__in=user.gestalt.groups.values('id')))))
        qs = qs.can_view(user, container='conversation')
        qs = qs.annotate(last_answer=Max('conversation__contributions__time_created'))
        qs = qs.annotate(last_comment=Max('content__contributions__time_created'))
        qs = qs.annotate(first_version=Min('content__versions__time_created'))
        qs = qs.annotate(last_activity=Coalesce(
            'last_answer',
            Greatest('first_version', Coalesce('last_comment', 'first_version'))))
        qs = qs.order_by('-last_activity')
        return qs

    def active_ordered_user_associations(self, user):
        qs = self
        qs = qs.ordered_user_associations(user)
        qs = qs.filter(last_activity__gte=user.gestalt.activity_bookmark_time)
        return qs
