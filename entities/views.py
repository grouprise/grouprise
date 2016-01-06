from django.contrib.auth import mixins as auth_mixins
from django.views import generic
from rules.contrib import views as rules_views

from . import models


class Gestalt(rules_views.PermissionRequiredMixin, generic.DetailView):
    model = models.Gestalt
    permission_required = 'entities.view_gestalt'


class GestaltSettings(rules_views.PermissionRequiredMixin, generic.TemplateView):
    permission_required = 'entities.change_gestalt'
    template_name = 'entities/gestalt_settings.html'


class GroupDetail(rules_views.PermissionRequiredMixin, generic.DetailView):
    model = models.Group
    permission_required = 'entities.view_group'


class GroupUpdate(rules_views.PermissionRequiredMixin, generic.UpdateView):
    fields = ['address', 'url', 'date_founded']
    model = models.Group
    permission_required = 'entities.change_group'
