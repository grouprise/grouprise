from django.urls import reverse
from django.utils.translation import gettext as _
import django.views.generic

from django.core.exceptions import ObjectDoesNotExist
from grouprise.core.views import PermissionMixin
from grouprise.features.groups.models import Group

from .models import MatrixChatGestaltSettings
from .settings import MATRIX_SETTINGS


class UpdateMatrixChatGestaltSettings(PermissionMixin, django.views.generic.FormView):
    permission_required = "gestalten.change"
    template_name = "matrix_chat/update_gestalt_settings.html"

    def get_form_class(self):
        # Avoid a direct assignment of "form_class", since that module requires an initialized
        # configuration.
        from .forms import MatrixChatGestaltSettingsForm
        return MatrixChatGestaltSettingsForm

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
        return "{}?group={}".format(reverse("matrix-chat-settings-user"), slug)

    def form_valid(self, form):
        gestalt = self.request.user.gestalt
        matrix_settings, created = MatrixChatGestaltSettings.objects.get_or_create(
            gestalt=gestalt
        )
        update_fields = []
        new_matrix_id = form.cleaned_data["matrix_id"]
        if matrix_settings.matrix_id_override != new_matrix_id:
            matrix_settings.matrix_id_override = new_matrix_id
            update_fields.append("matrix_id_override")
        matrix_settings.save(update_fields=update_fields)
        if created:
            gestalt.save()
        return super().form_valid(form)


class UpdateMatrixChatGroupSettings(PermissionMixin, django.views.generic.FormView):
    permission_required = "groups.change"
    template_name = "matrix_chat/update_group_settings.html"

    def get_form_class(self):
        # Avoid a direct assignment of "form_class", since that module requires an initialized
        # configuration.
        from .forms import MatrixChatGroupSettingsForm
        return MatrixChatGroupSettingsForm

    def get_group(self):
        return Group.objects.filter(slug=self.request.GET.get("group")).first()

    def get_group_rooms(self):
        return self.get_group().matrix_rooms.order_by("is_private")

    def get_permission_object(self):
        return self.get_group()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.get_group()
        return context

    def get_initial(self):
        initial = super().get_initial()
        for room in self.get_group_rooms():
            if room.is_private:
                initial["room_private_visibility"] = room.is_visible
                initial["room_private_matrix_reference"] = room.room_id
            else:
                initial["room_public_visibility"] = room.is_visible
                initial["room_public_matrix_reference"] = room.room_id
        return initial

    @property
    def success_url(self):
        return "{}?group={}".format(
            reverse("matrix-chat-settings-group"), self.get_group().slug
        )

    def form_valid(self, form):
        for room in self.get_group_rooms():
            update_fields = []
            if room.is_private:
                new_is_visible = form.cleaned_data["room_private_visibility"]
                new_room_id = form.cleaned_data["room_private_matrix_reference"]
            else:
                new_is_visible = form.cleaned_data["room_public_visibility"]
                new_room_id = form.cleaned_data["room_public_matrix_reference"]
            if room.is_visible != new_is_visible:
                room.is_visible = new_is_visible
                update_fields.append("is_visible")
            if room.room_id != new_room_id:
                room.room_id = new_room_id
                update_fields.append("room_id")
            room.save(update_fields=update_fields)
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
