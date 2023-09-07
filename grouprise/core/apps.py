import sys

from django.apps import AppConfig
from django.conf import settings
from setproctitle import setproctitle

from grouprise import __release__


def _register_startup_hooks():
    """register the startup hooks after the Django settings were at least partially resolved

    The startup hooks cannot be imported at the top level of this module, since the import of
    the `huey.contrib.djhuey` module relies on a properly populated settings store.

    Thus, we need to run `_resolve_django_settings` before importing `on_startup`.
    """
    from huey.contrib.djhuey import on_startup

    @on_startup()
    def _resolve_lazy_core_settings():
        """we need to ensure, that all settings are resolved (required for async tasks)

        Django (at least up to 4.x) does not allow ORM requests in async contexts.

        Most settings are probably populated in `_resolve_django_settings`.
        But some settings may remain unresolved at that (early) moment of app initialization.
        """
        from .settings import CORE_SETTINGS

        CORE_SETTINGS.resolve_lazy_settings()


def _set_process_title_for_tasks():
    """override the process name for "run_huey"

    This eases process tracking (e.g. via monit) and is simply more beautiful.

    This function is called within the context of *all* grouprise related processes.
    But for most processes, we can arrange the process title within the Django management script.
    Only huey's management script is used without a wrapper.
    Thus, we need to override its process title manually.

    This function must be called before any huey module is loaded.
    Otherwise consumer threads are spawned and some of the threads will carry the original
    `python3` name.
    """
    if "run_huey" in sys.argv:
        setproctitle("grouprise-tasks")


def _resolve_django_settings():
    from .settings import CORE_SETTINGS

    try:
        CORE_SETTINGS.resolve_lazy_settings()
    except Exception:
        # Resolution may fail under certain circumstances, e.g. during the initial run of
        # "migrate" (before the django site is written to the database).
        # We just hope, this works *almost* always.
        pass


def _configure_sentry():
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


class CoreConfig(AppConfig):
    name = "grouprise.core"

    def ready(self):
        self.module.autodiscover()
        _resolve_django_settings()
        _set_process_title_for_tasks()
        _register_startup_hooks()
        _configure_sentry()
