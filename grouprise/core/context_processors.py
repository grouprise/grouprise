from grouprise.core.settings import CORE_SETTINGS, get_grouprise_site


def settings(request):
    return {
        "GROUPRISE_CLAIMS": CORE_SETTINGS.CLAIMS,
        "GROUPRISE_HEADER_ITEMS": CORE_SETTINGS.HEADER_ITEMS,
        "GROUPRISE_FOOTER_ITEMS": CORE_SETTINGS.FOOTER_ITEMS,
        "GROUPRISE_SITE_NAME": get_grouprise_site().name,
        "GROUPRISE_THEME_COLOR": CORE_SETTINGS.THEME_COLOR,
        "GROUPRISE_LOGO_TEXT": CORE_SETTINGS.LOGO_TEXT,
        "GROUPRISE_LOGO_BACKDROP": CORE_SETTINGS.LOGO_BACKDROP,
        "GROUPRISE_LOGO_SQUARE": CORE_SETTINGS.LOGO_SQUARE,
        "GROUPRISE_LOGO_FAVICON": CORE_SETTINGS.LOGO_FAVICON,
    }
