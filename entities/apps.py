from django import apps


class EntitiesConfig(apps.AppConfig):
    name = 'entities'

    def ready(self):
        # side effect: registration of signals
        from . import signals    # noqa: F401
