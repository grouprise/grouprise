from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView

from grouprise.core.views import PermissionMixin
from grouprise.features.associations.models import Association


class ActivityView(PermissionMixin, ListView):
    model = Association
    permission_required = "associations.list_activity"
    template_name = "associations/list_activity.html"
    paginate_by = 12

    def get_queryset(self):
        return self.request.user.gestalt.notifications.order_by("-created_on")

    def post(self, *args, **kwargs):
        self.get_queryset().update(is_read=True)
        return HttpResponseRedirect(reverse("activity"))
