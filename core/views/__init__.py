import json
from .base import View  # NOQA
from .edit import CreateView as Create, FormView as Form  # NOQA
import utils.views


class Delete(utils.views.Delete):
    pass


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
