from django import apps


class ContentConfig(apps.AppConfig):
    name = 'content'

    def ready(self):
        from . import signals
