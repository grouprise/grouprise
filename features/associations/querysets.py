from django.db import models
from features.groups import models as groups


class Association(models.QuerySet):
    def can_view(self, user, **kwargs):
        if user.is_authenticated():
            gestalt_groups = groups.Group.objects.filter(memberships__member=user.gestalt)
            author_query_string = '{}__texts__author'.format(kwargs['container'])
            return self.filter(
                    models.Q(**{author_query_string: user.gestalt})
                    | (models.Q(entity_type=groups.GROUP_TYPE)
                        & models.Q(entity_id__in=gestalt_groups)))
        else:
            return self.none()
