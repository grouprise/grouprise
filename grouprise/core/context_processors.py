from django.contrib.sites.models import Site

from grouprise.core.settings import CORE_SETTINGS


def settings(request):
    return {
        "GROUPRISE_CLAIMS": CORE_SETTINGS.CLAIMS,
        "GROUPRISE_SITE_NAME": Site.objects.get_current().name,
        "GROUPRISE_THEME_COLOR": CORE_SETTINGS.THEME_COLOR,
        "GROUPRISE_LOGO_TEXT": CORE_SETTINGS.LOGO_TEXT,
        "GROUPRISE_LOGO_BACKDROP": CORE_SETTINGS.LOGO_BACKDROP,
        "GROUPRISE_LOGO_SQUARE": CORE_SETTINGS.LOGO_SQUARE,
        "GROUPRISE_LOGO_FAVICON": CORE_SETTINGS.LOGO_FAVICON,
    }
