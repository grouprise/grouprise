import django
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404

import core
import utils
from features import gestalten, groups
from features.content import views as content
from features.groups.models import Group


class Entity(core.views.PermissionMixin, django.views.generic.View):
    def get(self, request, *args, **kwargs):
        context = self.view.get_context_data(object=self.view.object)
        return self.view.render_to_response(context)

    def get_object(self):
        slug = self.kwargs.get('entity_slug')
        try:
            return Group.objects.get(slug=slug)
        except Group.DoesNotExist:
            return get_object_or_404(gestalten.models.Gestalt, user__username=slug)

    def get_view(self):
        # choose view based on entity type
        entity = self.get_object()
        if entity.is_group:
            view = groups.views.Detail()
        else:
            view = gestalten.views.Detail()

        # set view attributes
        view.object = entity
        view.object_list = None
        view.kwargs = self.kwargs
        view.request = self.request

        return view

    def has_permission(self):
        self.view = self.get_view()
        return self.view.has_permission()


class Index(content.List):
    template_name = 'stadt/index.html'

    def get_context_data(self, **kwargs):
        kwargs['town_name'] = get_current_site(self.request).name.split()[-1]
        return super().get_context_data(**kwargs)


class Privacy(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/privacy.html'
    title = 'Datenschutz'

    def get_context_data(self, **kwargs):
        kwargs['HAS_PIWIK'] = settings.HAS_PIWIK
        return super().get_context_data(**kwargs)
