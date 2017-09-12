from django.shortcuts import get_object_or_404

from features.associations.models import Association
from features.gestalten.models import Gestalt
from features.groups.models import Group


class AssociationMixin:
    def get_association(self):
        # determine entity
        try:
            entity_slug = self.kwargs.get('entity_slug')
            entity = Group.objects.get(slug=entity_slug)
        except Group.DoesNotExist:
            entity = get_object_or_404(Gestalt, user__username=entity_slug)

        # determine association
        association_slug = self.kwargs.get('association_slug')
        return get_object_or_404(
                Association, entity_type=entity.content_type, entity_id=entity.id,
                slug=association_slug)
