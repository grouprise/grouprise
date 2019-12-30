from django.conf import settings

from grouprise.core.settings import LazySettingsResolver


try:
    _EVENT_SETTINGS_RAW = settings.GROUPRISE["EVENTS"]
except (AttributeError, KeyError):
    _EVENT_SETTINGS_RAW = {}


EVENT_SETTINGS = LazySettingsResolver(
    ENABLE_REPETITIONS=_EVENT_SETTINGS_RAW.get("ENABLE_REPETITIONS", False),
)
