import json

import django

from rules.contrib.views import PermissionRequiredMixin


class PermissionMixin(PermissionRequiredMixin):
    @property
    def raise_exception(self):
        return self.request.user.is_authenticated


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
