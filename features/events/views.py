from content import models
from core.views import base
from django.views import generic


class List(base.PermissionMixin, generic.ListView):
    permission_required = 'events.view_list'
    template_name = 'events/list.html'
    paginate_by = 10

    def get_queryset(self):
        return models.Event.objects.can_view(self.request.user).upcoming()
