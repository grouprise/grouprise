from django.views import generic
from rules.contrib import views as rules_views

from . import models


class GestaltDetail(generic.DetailView):
    model = models.Gestalt


class GroupDetail(generic.DetailView):
    model = models.Group


class GroupUpdate(rules_views.PermissionRequiredMixin, generic.UpdateView):
    fields = ['address', 'url', 'date_founded']
    model = models.Group
    permission_required = 'entities.change_group'
