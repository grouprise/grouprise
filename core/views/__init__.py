import django
import json

import utils.views
from .base import PermissionMixin, View  # NOQA
from .edit import CreateView as Create, FormView as Form  # NOQA


class Delete(utils.views.Delete):
    pass


class Error(django.views.generic.View):
    def dispatch(self, *args, **kwargs):
        raise RuntimeError('Intentionally raised an error!')


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
