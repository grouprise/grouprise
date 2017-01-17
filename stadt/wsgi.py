"""
WSGI config for stadt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stadt.settings")

# If this environment variable is set, then a file containing a profile dump is stored for the
# processing of every single request.
if os.environ.get("PROFILING_DIRECTORY"):
    from werkzeug.contrib.profiler import ProfilerMiddleware
    application = ProfilerMiddleware(
        get_wsgi_application(), profile_dir=os.environ["PROFILING_DIRECTORY"])
else:
    application = get_wsgi_application()
