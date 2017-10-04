import django
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

import core
from features.associations.models import Association
from features.gestalten.models import Gestalt
from features.groups.models import Group
from . import models


def get_association_or_404(**kwargs):
    association = get_object_or_404(Association, **kwargs)
    if association.deleted:
        raise Http404('The Association was deleted.')
    return association


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
        return get_association_or_404(
                entity_type=entity.content_type, entity_id=entity.id, slug=association_slug)


class Delete(AssociationMixin, core.views.PermissionMixin, django.views.generic.UpdateView):
    permission_required = 'associations.delete'
    model = models.Association
    fields = []
    template_name = 'associations/delete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'].deleted = now()
        kwargs['instance'].slug = None
        return kwargs

    def get_object(self):
        return self.get_association()

    def get_success_url(self):
        return self.object.entity.get_absolute_url()
