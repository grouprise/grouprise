from django import apps


class ContentConfig(apps.AppConfig):
    name = 'content'

    def ready(self):
        # side effect: registration of signals
        from . import signals    # noqa: F401
