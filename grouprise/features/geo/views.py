from django.contrib.contenttypes.models import ContentType
import django.views.generic
from django.urls import reverse
from django.utils.translation import gettext as _

from grouprise.core.views import PermissionMixin
from grouprise.features.groups.models import Group
from .forms import LocationForm
from .models import Location


class LocationView(PermissionMixin, django.views.generic.FormView):
    form_class = LocationForm
    locatable_template_variable = None

    def get_locatable(self):
        raise NotImplementedError()

    def get_fk_data(self):
        locatable = self.get_locatable()
        locatable_type = ContentType.objects.get_for_model(type(locatable))
        locatable_id = locatable.pk
        return locatable_type, locatable_id

    def get_permission_object(self):
        return self.get_locatable()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.locatable_template_variable:
            context[self.locatable_template_variable] = self.get_locatable()
        return context

    def get_initial(self):
        initial = super().get_initial()
        locatable_type, locatable_id = self.get_fk_data()
        try:
            initial["point"] = Location.objects.get(
                locatable_type=locatable_type, locatable_id=locatable_id
            ).point
        except Location.DoesNotExist:
            pass
        return initial

    def form_valid(self, form):
        locatable_type, locatable_id = self.get_fk_data()
        Location.objects.update_or_create(
            locatable_type=locatable_type,
            locatable_id=locatable_id,
            defaults={"point": form.cleaned_data["point"]},
        )
        return super().form_valid(form)


class UpdateGroupLocationSettings(LocationView):
    permission_required = "groups.change"
    template_name = "geo/update_group_settings.html"
    form_class = LocationForm
    locatable_template_variable = "group"

    def get_locatable(self):
        return Group.objects.filter(slug=self.request.GET.get("group")).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["help"] = _("Click on the map to select a location for your group.")
        return context

    @property
    def success_url(self):
        return "{}?group={}".format(
            reverse("geo-settings-group"), self.get_locatable().slug
        )
