from .default import TEMPLATES

DEBUG = True

TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG

# Email
# https://docs.djangoproject.com/en/1.9/topics/email/
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
