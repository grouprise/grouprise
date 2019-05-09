from django import apps


class TagsConfig(apps.AppConfig):
    name = 'grouprise.features.tags'

    def ready(self):
        from . import signals
        signals.Index.build()
