import django
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import ListView

import grouprise.core
from grouprise.core.views import PermissionMixin
from grouprise.features.associations.models import Association
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from . import models


def get_association_or_404(**kwargs):
    association = get_object_or_404(Association, **kwargs)
    if association.deleted:
        raise Http404("The Association was deleted.")
    return association


class AssociationMixin:
    def get_association(self):
        # determine entity
        try:
            entity_slug = self.kwargs.get("entity_slug")
            entity = Group.objects.get(slug=entity_slug)
        except Group.DoesNotExist:
            entity = get_object_or_404(Gestalt, user__username=entity_slug)

        # determine association
        association_slug = self.kwargs.get("association_slug")
        return get_association_or_404(
            entity_type=entity.content_type, entity_id=entity.id, slug=association_slug
        )


class ActivityView(PermissionMixin, ListView):
    model = Association
    permission_required = "associations.list_activity"
    template_name = "associations/list_activity.html"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().ordered_user_associations(self.request.user)

    def post(self, *args, **kwargs):
        self.request.user.gestalt.activity_bookmark_time = now()
        self.request.user.gestalt.save()
        return HttpResponseRedirect(reverse("activity"))


class Delete(
    AssociationMixin,
    grouprise.core.views.PermissionMixin,
    django.views.generic.UpdateView,
):
    permission_required = "associations.delete"
    model = models.Association
    fields = []
    template_name = "associations/delete.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"].deleted = now()
        if self.request.method.lower() == "post":
            kwargs["instance"].slug = None
        return kwargs

    def get_object(self):
        return self.get_association()

    def get_success_url(self):
        return self.object.entity.get_profile_url()
