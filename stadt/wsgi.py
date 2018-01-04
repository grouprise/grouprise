"""
WSGI config for stadt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stadt.settings")

application = get_wsgi_application()

ENABLE_SENTRY = os.environ.get("SENTRY_ENABLE", "false") == "true"
if ENABLE_SENTRY:
    from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
    application = Sentry(application)

PROFILING_DIR = os.environ.get("PROFILING_DIRECTORY", False)
if PROFILING_DIR:
    from werkzeug.contrib.profiler import ProfilerMiddleware
    application = ProfilerMiddleware(application, profile_dir=PROFILING_DIR)
