from django.conf import settings

from grouprise.core.settings import LazySettingsResolver

try:
    _TAG_SETTINGS = settings.GROUPRISE["TAGS"]
except (KeyError, AttributeError):
    _TAG_SETTINGS = {}


TAG_SETTINGS = LazySettingsResolver(
    FEATURED_TAG_IDS=_TAG_SETTINGS.get("FEATURED_TAG_IDS", []),
)
