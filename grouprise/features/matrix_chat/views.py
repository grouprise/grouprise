from django.urls import reverse
from django.utils.translation import gettext as _
import django.views.generic

from django.core.exceptions import ObjectDoesNotExist
from grouprise.core.views import PermissionMixin
from grouprise.features.groups.models import Group

from .forms import MatrixChatGestaltSettingsForm
from .models import MatrixChatGestaltSettings
from .settings import MATRIX_SETTINGS


class UpdateMatrixChatGestaltSettings(PermissionMixin, django.views.generic.FormView):
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


class ShowMatrixChatHelp(django.views.generic.TemplateView):
    template_name = "matrix_chat/help.html"
    title = _("Chat / Instant Messaging")

    def get_context_data(self, **kwargs):
        kwargs["MATRIX_DOMAIN"] = MATRIX_SETTINGS.DOMAIN
        kwargs["help_matrix_url"] = "https://matrix.org/faq/#usage"
        kwargs["help_element_url"] = "https://element.io/help"
        kwargs["matrix_url"] = "https://matrix.org/"
        kwargs["element_url"] = "https://github.com/vector-im/element-web"
        kwargs[
            "element_android_url"
        ] = "https://matrix.org/docs/projects/client/element-android"
        kwargs["grouprise_url"] = "https://grouprise.org/"
        kwargs["free_software_url"] = "https://www.gnu.org/philosophy/free-sw.html"
        kwargs["matrix_clients_url"] = "https://matrix.org/clients/"
        kwargs["matrix_client_path"] = "/stadt/chat/"
        return super().get_context_data(**kwargs)
