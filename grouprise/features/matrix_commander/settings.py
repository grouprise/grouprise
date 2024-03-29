from django.conf import settings

from grouprise.core.settings import LazySettingsResolver, get_grouprise_site
from grouprise.settings_loader import MatrixBackend


try:
    _SETTINGS = settings.GROUPRISE["MATRIX_COMMANDER"]
except (KeyError, AttributeError):
    _SETTINGS = {}


MATRIX_COMMANDER_SETTINGS = LazySettingsResolver(
    ENABLED=_SETTINGS.get("ENABLED", False),
    BOT_ID=lambda: _SETTINGS.get(
        "BOT_ID", f"@grouprise-commander-bot:{get_grouprise_site()}"
    ),
    BOT_ACCESS_TOKEN=_SETTINGS.get("BOT_ACCESS_TOKEN", None),
    BACKEND=_SETTINGS.get("BACKEND", MatrixBackend.NIO),
    ADMIN_ROOMS=_SETTINGS.get("ADMIN_ROOMS", []),
)
