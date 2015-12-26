from django import apps


class EntitiesConfig(apps.AppConfig):
    name = 'entities'

    def ready(self):
        from . import signals
