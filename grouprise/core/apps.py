from django.apps import AppConfig
from django.conf import settings

from grouprise import __release__


class CoreConfig(AppConfig):
    name = "grouprise.core"

    def ready(self):
        self.module.autodiscover()

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
