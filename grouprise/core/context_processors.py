from django.contrib.sites.models import Site

import grouprise.core.settings as grouprise_settings


def settings(request):
    return {
        "GROUPRISE_CLAIMS": grouprise_settings.CLAIMS,
        "GROUPRISE_SITE_NAME": Site.objects.get_current().name,
        "GROUPRISE_THEME_COLOR": grouprise_settings.THEME_COLOR,
        "GROUPRISE_LOGO_TEXT": grouprise_settings.LOGO_TEXT,
        "GROUPRISE_LOGO_BACKDROP": grouprise_settings.LOGO_BACKDROP,
        "GROUPRISE_LOGO_SQUARE": grouprise_settings.LOGO_SQUARE,
        "GROUPRISE_LOGO_FAVICON": grouprise_settings.LOGO_FAVICON,
    }
