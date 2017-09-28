import django
from django.shortcuts import get_object_or_404

import core
import utils
from features import gestalten, groups
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


class Imprint(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'


class Privacy(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/privacy.html'
    title = 'Datenschutz'
