from django.apps import AppConfig


class FragmentsConfig(AppConfig):
    name = 'core.fragments'


class AutodiscoverFragmentsConfig(FragmentsConfig):
    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('fragments')
