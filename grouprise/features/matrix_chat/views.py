from django.urls import reverse
from django.views.generic import FormView

from django.core.exceptions import ObjectDoesNotExist
from grouprise.core.views import PermissionMixin
from grouprise.features.groups.models import Group

from .forms import MatrixChatGestaltSettingsForm
from .models import MatrixChatGestaltSettings


class UpdateMatrixChatGestaltSettings(PermissionMixin, FormView):
    permission_required = "gestalten.change"
    form_class = MatrixChatGestaltSettingsForm
    template_name = "matrix_chat/update_settings.html"

    def get_group(self):
        return Group.objects.filter(slug=self.request.GET.get("group")).first()

    def get_permission_object(self):
        return self.request.user.gestalt

    def get_context_data(self, **kwargs):
        group = self.get_group()
        if group:
            kwargs["group"] = group
        return super().get_context_data(**kwargs)

    def get_initial(self):
        result = {}
        try:
            matrix_settings = self.request.user.gestalt.matrix_chat_settings
            result["matrix_id"] = matrix_settings.matrix_id_override
        except ObjectDoesNotExist:
            pass
        return result

    @property
    def success_url(self):
        group = self.get_group()
        slug = group.slug if group else ""
        return "{}?group={}".format(reverse("matrix-chat-settings"), slug)

    def form_valid(self, form):
        gestalt = self.request.user.gestalt
        matrix_settings = MatrixChatGestaltSettings.objects.get_or_create(
            gestalt=gestalt
        )[0]
        matrix_settings.matrix_id_override = form.cleaned_data["matrix_id"]
        matrix_settings.save()
        gestalt.save()
        return super().form_valid(form)
