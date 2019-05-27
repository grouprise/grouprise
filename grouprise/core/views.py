import json

import django
from django_filters.views import FilterMixin

from rules.contrib.views import PermissionRequiredMixin


class PermissionMixin(PermissionRequiredMixin):
    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


class TemplateFilterMixin(FilterMixin):
    def get_context_data(self, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if not self.filterset.is_bound or self.filterset.is_valid() or not self.get_strict():
            self.object_list = self.filterset.qs
        else:
            self.object_list = self.filterset.queryset.none()

        return super().get_context_data(
                filter=self.filterset, object_list=self.object_list,
                show_filter=bool(self.object_list or self.filterset.is_bound))


class AppConfig:
    def __init__(self):
        self._settings = {}
        self._defaults = {}

    def add_setting(self, name, value):
        self._settings[name] = value
        return self

    def add_default(self, name, value):
        self._defaults[name] = value
        return self

    def serialize(self):
        conf = {}
        conf.update(self._defaults)
        conf.update(self._settings)
        return json.dumps(conf)


app_config = AppConfig()


class Markdown(django.views.generic.TemplateView):
    template_name = 'core/markdown.html'
