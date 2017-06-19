import django

import entities
from features.gestalten import models as gestalten
from features.groups import models as groups


class Entity(django.views.generic.View):
    def get(self, request, *args, **kwargs):
        try:
            entity = groups.Group.objects.get(slug=kwargs.get('entity_slug'))
            view = entities.views.Group()
        except groups.Group.DoesNotExist:
            entity = django.shortcuts.get_object_or_404(
                    gestalten.Gestalt, user__username=kwargs.get('entity_slug'))
            view = entities.views.Gestalt()
        view.request = request
        view.kwargs = kwargs
        view.object = entity
        return view.get(request, *args, **kwargs)
