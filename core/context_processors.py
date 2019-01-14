import django
from django.conf import settings as django_settings
from django.contrib.sites import shortcuts


def settings(request):
    return {
        'STADTGESTALTEN_CLAIMS': django_settings.GROUPRISE.get('CLAIMS', [])
    }


def site(request):
    return {
        'http_origin': request.build_absolute_uri("/").rstrip("/"),
        'site': shortcuts.get_current_site(request),
    }
