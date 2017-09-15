from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.utils import module_loading

        for module_name in ['assets', 'fragments', 'markdown', 'rest_api', 'signals']:
            module_loading.autodiscover_modules(module_name)
