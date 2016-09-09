from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.utils import module_loading
        module_loading.import_string(
                settings.ROOT_SIGNALCONF + '.connections')
