import sys

from django.apps import AppConfig
from django.conf import settings
from setproctitle import setproctitle

from grouprise import __release__


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
        from .settings import CORE_SETTINGS

        self.module.autodiscover()
        _set_process_title_for_tasks()
        _configure_sentry()
        # During the startup of management commands (e.g. matrix-commander) a sync/async context
        # problem may occur.
        CORE_SETTINGS.resolve_lazy_settings()
