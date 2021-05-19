from django.conf import settings
from django.contrib.sites.models import Site

from grouprise.core.settings import LazySettingsResolver


_MATRIX_SETTINGS = settings.GROUPRISE.get("MATRIX_CHAT", {})


MATRIX_SETTINGS = LazySettingsResolver(
    ENABLED=_MATRIX_SETTINGS.get("ENABLED", False),
    DOMAIN=_MATRIX_SETTINGS.get("DOMAIN", lambda: Site.objects.get_current().domain),
    ADMIN_API_URL=_MATRIX_SETTINGS.get("ADMIN_API_URL", "http://localhost:8008"),
    BOT_USERNAME=_MATRIX_SETTINGS.get("BOT_USERNAME", "grouprise-bot"),
    BOT_ACCESS_TOKEN=_MATRIX_SETTINGS.get("BOT_ACCESS_TOKEN", None),
)
