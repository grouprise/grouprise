from . import models
from core.views import base
from django.views import generic


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True).order_by('-score')
    template_name = 'gestalten/list.html'
    paginate_by = 10
