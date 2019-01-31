from django.conf import settings as django_settings
from django.contrib.sites.models import Site


def settings(request):
    return {
        'GROUPRISE_CLAIMS': django_settings.GROUPRISE.get('CLAIMS', []),
        'GROUPRISE_SITE_NAME': Site.objects.get_current().name,
    }
