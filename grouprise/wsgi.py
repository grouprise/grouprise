"""
WSGI config for stadt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grouprise.settings")

application = get_wsgi_application()

# configure sentry if DSN has been defined
if settings.SENTRY_DSN:
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

    application = SentryWsgiMiddleware(application)

PROFILING_DIR = os.environ.get("PROFILING_DIRECTORY", False)
if PROFILING_DIR:
    from werkzeug.contrib.profiler import ProfilerMiddleware

    application = ProfilerMiddleware(application, profile_dir=PROFILING_DIR)
