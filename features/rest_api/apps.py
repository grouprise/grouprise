import importlib
from django.apps import AppConfig


class RestApiConfig(AppConfig):
    label = 'rest_api'
    name = 'features.rest_api'
    verbose_name = 'Stadtgestalten API'

    def ready(self):
        from django.apps import apps
        for config in apps.get_app_configs():
            try:
                importlib.import_module("%s.rest_api" % config.name)
            except ImportError:
                pass
