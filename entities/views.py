from . import models
from crispy_forms import bootstrap, layout
from django.contrib.auth import mixins as auth_mixins
from django.contrib.sites import shortcuts
from django.views import generic
from rules.contrib import views as rules_views
from util import views as util_views


class Gestalt(rules_views.PermissionRequiredMixin, generic.DetailView):
    model = models.Gestalt
    permission_required = 'entities.view_gestalt'


class GestaltSettings(rules_views.PermissionRequiredMixin, generic.TemplateView):
    permission_required = 'entities.change_gestalt'
    template_name = 'entities/gestalt_settings.html'


class GroupDetail(rules_views.PermissionRequiredMixin, generic.DetailView):
    model = models.Group
    permission_required = 'entities.view_group'


class GroupUpdate(rules_views.PermissionRequiredMixin, util_views.LayoutMixin, generic.UpdateView):
    fields = ['address', 'date_founded', 'name', 'slug', 'url']
    model = models.Group
    permission_required = 'entities.change_group'

    def get_layout(self):
        DOMAIN = shortcuts.get_current_site(self.request).domain
        return [
                'name',
                layout.Field('address', rows=4),
                'url',
                layout.Field('date_founded', data_provide='datepicker',
                    data_date_language='de', data_date_min_view_mode='months',
                    data_date_start_view='decade'),
                bootstrap.PrependedText('slug', '%(domain)s/' % {'domain': DOMAIN }),
                bootstrap.FormActions(layout.Submit('submit', 'Angaben speichern')),
                ]
