import os

from django.conf import settings
from django.templatetags.static import static


_GR = settings.GROUPRISE


# branding
CLAIMS = _GR.get("CLAIMS", [])
LOGO_BACKDROP = _GR.get(
    "BRANDING_LOGO_BACKDROP", static("core/logos/logo-backdrop.svg")
)
LOGO_FAVICON = _GR.get("BRANDING_LOGO_FAVICON", static("core/logos/logo-square.png"))
LOGO_SQUARE = _GR.get("BRANDING_LOGO_SQUARE", static("core/logos/logo-square.svg"))
LOGO_TEXT = _GR.get("BRANDING_LOGO_TEXT", static("core/logos/logo-text.svg"))
THEME_COLOR = _GR.get("BRANDING_THEME_COLOR", "#2a62ac")

# mail handling
COLLECTOR_MAILBOX_ADDRESS = _GR.get("COLLECTOR_MAILBOX_ADDRESS", None)
DEFAULT_DISTINCT_FROM_EMAIL = _GR.get(
    "DEFAULT_DISTINCT_FROM_EMAIL", "noreply+{slug}@localhost"
)
DEFAULT_REPLY_TO_EMAIL = _GR.get(
    "DEFAULT_REPLY_TO_EMAIL", "reply+{reply_key}@localhost"
)
MAILINGLIST_ENABLED = _GR.get("MAILINGLIST_ENABLED", False)
POSTMASTER_EMAIL = _GR.get("POSTMASTER_EMAIL", "postmaster@localhost")

# content import
FEED_IMPORTER_GESTALT_ID = _GR.get("FEED_IMPORTER_GESTALT_ID", None)
OPERATOR_GROUP_ID = _GR.get("OPERATOR_GROUP_ID", 1)
UNKNOWN_GESTALT_ID = _GR.get("UNKNOWN_GESTALT_ID", 1)

# local administration
BACKUP_PATH = _GR.get("BACKUP_PATH", os.getcwd())
HOOK_SCRIPT_PATHS = _GR.get("HOOK_SCRIPT_PATHS", [])

# miscellaneous
ENTITY_SLUG_BLACKLIST = _GR.get(
    "ENTITY_SLUG_BLACKLIST",
    [
        "all",
        "grouprise",
        "info",
        "mail",
        "noreply",
        "postmaster",
        "reply",
        "stadt",
        "webmaster",
        "www",
    ],
)
SCORE_CONTENT_AGE = _GR.get("SCORE_CONTENT_AGE", 100)
UPLOAD_MAX_FILE_SIZE = _GR.get("UPLOAD_MAX_FILE_SIZE", 10)
