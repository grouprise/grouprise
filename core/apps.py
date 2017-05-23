from django.apps import AppConfig
from django.conf import settings


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.utils import module_loading
        module_loading.import_string(
                settings.ROOT_SIGNALCONF + '.connections')
        module_loading.autodiscover_modules('fragments')
        module_loading.autodiscover_modules('rest_api')
        module_loading.autodiscover_modules('markdown')
        module_loading.autodiscover_modules('signals')
        module_loading.autodiscover_modules('assets')
