from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.templatetags.static import static


def settings(request):
    gr_settings = django_settings.GROUPRISE
    return {
        'GROUPRISE_CLAIMS': gr_settings.get('CLAIMS', []),
        'GROUPRISE_SITE_NAME': Site.objects.get_current().name,
        'GROUPRISE_THEME_COLOR': gr_settings.get('BRANDING_THEME_COLOR', '#2a62ac'),
        'GROUPRISE_LOGO_TEXT': gr_settings.get(
            'BRANDING_LOGO_TEXT', static('core/logos/logo-text.svg')),
        'GROUPRISE_LOGO_BACKDROP': gr_settings.get(
            'BRANDING_LOGO_BACKDROP', static('core/logos/logo-backdrop.svg')),
        'GROUPRISE_LOGO_SQUARE': gr_settings.get(
            'BRANDING_LOGO_SQUARE', static('core/logos/logo-square.svg')),
        'GROUPRISE_LOGO_FAVICON': gr_settings.get(
            'BRANDING_LOGO_FAVICON', static('core/logos/logo-square.png')),
    }
