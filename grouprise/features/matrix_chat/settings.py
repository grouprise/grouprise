from django.conf import settings

from grouprise.core.settings import LazySettingsResolver, get_grouprise_site


try:
    _MATRIX_SETTINGS = settings.GROUPRISE["MATRIX_CHAT"]
except (KeyError, AttributeError):
    _MATRIX_SETTINGS = {}


MATRIX_SETTINGS = LazySettingsResolver(
    ENABLED=_MATRIX_SETTINGS.get("ENABLED", False),
    DOMAIN=_MATRIX_SETTINGS.get("DOMAIN", lambda: get_grouprise_site().domain),
    ADMIN_API_URL=_MATRIX_SETTINGS.get("ADMIN_API_URL", "http://localhost:8008"),
    BOT_USERNAME=_MATRIX_SETTINGS.get("BOT_USERNAME", "grouprise-bot"),
    BOT_ACCESS_TOKEN=_MATRIX_SETTINGS.get("BOT_ACCESS_TOKEN", None),
)
