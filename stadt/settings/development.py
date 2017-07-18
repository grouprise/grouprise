from .default import TEMPLATES

DEBUG = True

# Sorl Thumbnail image processing
# http://sorl-thumbnail.readthedocs.org/
THUMBNAIL_DEBUG = DEBUG

# TEMPLATE_DEBUG is officially deprecated in Django but still
# required by sorl-thumbnail.
TEMPLATE_DEBUG = DEBUG
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# Email
# https://docs.djangoproject.com/en/1.9/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
