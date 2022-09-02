from django.apps import AppConfig
from django.conf import settings
from huey.contrib.djhuey import on_startup

from grouprise import __release__


@on_startup()
def _resolve_lazy_core_settings():
    """we need to ensure, that all settings are resolved (required for async tasks)

    Django (at least up to 4.x) does not allow ORM requests in async contexts.
    """
    from .settings import CORE_SETTINGS

    CORE_SETTINGS.resolve_lazy_settings()


class CoreConfig(AppConfig):
    name = "grouprise.core"

    def ready(self):
        self.module.autodiscover()

        from .settings import CORE_SETTINGS

        try:
            CORE_SETTINGS.resolve_lazy_settings()
        except Exception:
            # Resolution may fail under certain circumstances, e.g. during the initial run of
            # "migrate" (before the django site is written to the database).
            # We just hope, this works *almost* always.
            pass

        # configure sentry if DSN has been defined
        sentry_dsn = getattr(settings, "SENTRY_DSN", None)
        if sentry_dsn:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration

            init_options = {
                "integrations": [DjangoIntegration()],
                "send_default_pii": True,
                "release": f"grouprise@{__release__}",
            }
            init_options.update(getattr(settings, "SENTRY_INIT_OPTIONS", {}))
            sentry_sdk.init(dsn=sentry_dsn, **init_options)
