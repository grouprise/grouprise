from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.utils.module_loading import autodiscover_modules

        for module_name in ['rules', 'signals']:
            autodiscover_modules(module_name)
