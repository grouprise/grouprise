import django
from django.contrib.sites import shortcuts


def settings(request):
    return {
            'STADTGESTALTEN_LOGO_URL': django.conf.settings.STADTGESTALTEN_LOGO_URL,
            'STADTGESTALTEN_SHOW_HEADER': django.conf.settings.STADTGESTALTEN_SHOW_HEADER,
            }


def site(request):
    return {
        'http_origin': request.build_absolute_uri("/").rstrip("/"),
        'site': shortcuts.get_current_site(request),
    }
