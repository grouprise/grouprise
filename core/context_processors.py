from django.conf import settings as django_settings
from django.contrib.sites import shortcuts


def settings(request):
    return {
        'GROUPRISE_CLAIMS': django_settings.GROUPRISE.get('CLAIMS', [])
    }


def site(request):
    return {
        'site': shortcuts.get_current_site(request),
    }
