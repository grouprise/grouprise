import django

import utils
from features import gestalten, groups


class Entity(django.views.generic.View):
    def get(self, request, *args, **kwargs):
        try:
            entity = groups.models.Group.objects.get(slug=kwargs.get('entity_slug'))
            view = groups.views.Group()
        except groups.models.Group.DoesNotExist:
            entity = django.shortcuts.get_object_or_404(
                    gestalten.models.Gestalt, user__username=kwargs.get('entity_slug'))
            view = gestalten.views.Detail()
        view.request = request
        view.kwargs = kwargs
        view.object = entity
        return view.get(request, *args, **kwargs)


class Imprint(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/imprint.html'
    title = 'Impressum'


class Privacy(utils.views.PageMixin, django.views.generic.TemplateView):
    permission_required = 'entities.view_imprint'
    template_name = 'entities/privacy.html'
    title = 'Datenschutz'
