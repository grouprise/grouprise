from django import apps


class TagsConfig(apps.AppConfig):
    name = 'features.tags'

    def ready(self):
        from . import signals
        signals.Index.build()
