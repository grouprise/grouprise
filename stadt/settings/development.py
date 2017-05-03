from .default import TEMPLATES

DEBUG = True

# Sorl Thumbnail image processing
# http://sorl-thumbnail.readthedocs.org/
THUMBNAIL_DEBUG = DEBUG

# _nach_ dem Laden der lokalen Einstellungen: Debug-Flags final setzen
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
