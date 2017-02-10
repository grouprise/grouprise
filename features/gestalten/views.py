from . import models
from core.views import base
from django.views import generic


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    menu = 'gestalt'
    queryset = models.Gestalt.objects.filter(public=True).order_by('-score')
    template_name = 'entities/gestalt_list.html'
    title = 'Gestalten'
