from django.apps import AppConfig
from django.conf import settings

from grouprise import __release__


class CoreConfig(AppConfig):
    name = 'grouprise.core'

    def ready(self):
        self.module.autodiscover()

        # configure sentry if DSN has been defined
        if settings.SENTRY_DSN:
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[DjangoIntegration()],
                send_default_pii=True,
                environment=settings.ENVIRONMENT,
                release=f'grouprise@{__release__}',
            )
