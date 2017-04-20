from django.views import generic

from core.views import base
from features.associations import models as associations
from . import models

class List(base.PermissionMixin, generic.ListView):
    permission_required = 'gestalten.view_list'
    queryset = models.Gestalt.objects.filter(public=True)
    ordering = '-score'
    paginate_by = 10
    template_name = 'gestalten/list.html'

    def get_content(self):
        return associations.Association.objects.filter(
                entity_type=models.Gestalt.get_content_type()).can_view(self.request.user)
