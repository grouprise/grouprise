import json
import logging
import urllib.request

from asgiref.sync import async_to_sync
import django.views.generic
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _

from grouprise.core.views import PermissionMixin
from grouprise.features.groups.models import Group

from .matrix_bot import ChatBot
from .models import MatrixChatGestaltSettings, MatrixChatGroupRoom
from .settings import MATRIX_SETTINGS

logger = logging.getLogger(__name__)


def get_room_url_for_requester(room_id, request_user):
    matrix_domain = MATRIX_SETTINGS.DOMAIN
    # determine the matrix domain of the requesting user
    if request_user.is_authenticated:
        try:
            user_matrix_id = request_user.gestalt.matrix_chat_settings.matrix_id
        except ObjectDoesNotExist:
            # no matrix settings are stored for the user
            pass
        else:
            if ":" in user_matrix_id:
                matrix_domain = user_matrix_id.lower().split(":", 1)[1]
    base_path = get_web_client_url_pattern_for_domain(matrix_domain)

    # We need to refer to the room alias (instead of the room ID), since Matrix room IDs are
    # supposed to be implementation details and should not be used in public.
    # See https://github.com/vector-im/element-web/issues/2925
    async def retrieve_room_alias():
        async with ChatBot() as bot:
            return await bot.get_public_room_name(room_id)

    room_alias = async_to_sync(retrieve_room_alias)()
    room_name = room_id if room_alias is None else room_alias
    return base_path.format(room=room_name)


def get_web_client_url_pattern_for_domain(domain):
    """determine the web client URL format string for a matrix domain

    The resulting string contains '{room}' in order to allow string formatting with the 'room'
    keyword.
    """
    if domain == MATRIX_SETTINGS.DOMAIN:
        # this path is handled by our external web proxy
        return "/stadt/chat/#/room/{room}"
    # try to determine the homeserver of the domain
    try:
        client_data = urllib.request.urlopen(
            f"https://{domain}/.well-known/matrix/client"
        ).read()
        homeserver_url = json.loads(client_data)["m.homeserver"]["base_url"]
    except (IOError, ValueError) as exc:
        logger.info(
            "Failed to retrieve '/.well-known/matrix/client' for domain '%s': %s",
            domain,
            exc,
        )
        homeserver_url = f"https://{domain}:8448"
    # try to retrieve the announced web client (e.g. via synapse's "webclient" interface)

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(f"{homeserver_url}/_matrix/client/")
    except urllib.error.HTTPError as exc:
        if exc.status == 302:
            web_client_url = exc.headers.get("location")
            return web_client_url.rstrip("/") + "/#/room/{room}"
    # Fall back to the matrix.to service for now.
    # In the future we may want to use the new matrix scheme:
    #   https://github.com/matrix-org/matrix-doc/pull/2312
    return "https://matrix.to/#/{room}"


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


class ShowMissingWebClientWarning(django.views.generic.TemplateView):
    template_name = "matrix_chat/missing_web_client.html"


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


class RedirectToMatrixRoomGroupPrivate(
    PermissionMixin, django.views.generic.RedirectView
):
    permission_required = "content.group_create"
    is_private = True

    def get_group_room(self):
        group = get_object_or_404(Group, slug=self.kwargs.get("group_slug"))
        return MatrixChatGroupRoom.objects.filter(
            group=group, is_private=self.is_private
        ).first()

    def get_redirect_url(self, *args, **kwargs):
        room = self.get_group_room()
        return get_room_url_for_requester(room.room_id, self.request.user)


class RedirectToMatrixRoomGroupPublic(RedirectToMatrixRoomGroupPrivate):
    permission_required = "content.list"
    is_private = False


class RedirectToMatrixRoomPublicFeed(django.views.generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        try:
            room_id = MATRIX_SETTINGS.PUBLIC_LISTENER_ROOMS[0]
        except IndexError:
            raise Http404("No public matrix chat room is configured")
        else:
            return get_room_url_for_requester(room_id, self.request.user)
