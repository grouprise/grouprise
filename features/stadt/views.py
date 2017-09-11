import django

import core
import utils
from features import gestalten, groups


class Entity(core.views.PermissionMixin, django.views.generic.View):
    def get(self, request, *args, **kwargs):
        return self.view.get(request, *args, **kwargs)

    def get_view(self):
        entity_slug = self.kwargs.get('entity_slug')
        try:
            entity = groups.models.Group.objects.get(slug=entity_slug)
            view = groups.views.Group()
            view.related_object = entity
        except groups.models.Group.DoesNotExist:
            entity = django.shortcuts.get_object_or_404(
                    gestalten.models.Gestalt, user__username=entity_slug)
            view = gestalten.views.Detail()
            view.object = entity
        return view

    def has_permission(self):
        self.view = self.get_view()
        self.view.request = self.request
        self.view.kwargs = self.kwargs
        return self.view.has_permission()


class Imprint(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'


class Privacy(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/privacy.html'
    title = 'Datenschutz'
