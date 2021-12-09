from django.conf import settings

from grouprise.core.settings import LazySettingsResolver

try:
    _EVENT_SETTINGS_RAW = settings.GROUPRISE["EVENTS"]
except (AttributeError, KeyError):
    _EVENT_SETTINGS_RAW = {}


EVENT_SETTINGS = LazySettingsResolver(
    ENABLE_REPETITIONS=_EVENT_SETTINGS_RAW.get("ENABLE_REPETITIONS", False),
    ENABLE_ATTENDANCE=_EVENT_SETTINGS_RAW.get("ENABLE_ATTENDANCE", False),
    ALLOW_ATTENDANCE_MANAGEMENT_FOR_GROUP_MEMBERS=_EVENT_SETTINGS_RAW.get(
        "ALLOW_ATTENDANCE_MANAGEMENT_FOR_GROUP_MEMBERS", False
    ),
)
