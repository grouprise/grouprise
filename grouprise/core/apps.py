from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'grouprise.core'

    def ready(self):
        self.module.autodiscover()
