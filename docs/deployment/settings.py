# grouprise settings file
# see https://docs.djangoproject.com/en/2.1/ref/settings/

import os
import subprocess
from stadt.settings.default import *
from grouprise.core.assets import add_javascript_reference, add_javascript_inline, add_csp_directive, add_meta

# see https://www.miniwebtool.com/django-secret-key-generator/
SECRET_KEY = 'CHANGE THIS!'
ALLOWED_HOSTS = ['yourhostname.org', 'localhost']

# dies wird von nginx gesetzt
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_SSL_REDIRECT = False
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = False
# X_FRAME_OPTIONS = 'DENY'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'grouprise',
        'USER': 'grouprise',
        'PASSWORD': 'xxxxx',
    }
}


ADMINS = [
    ('Admins', 'mail@example.org'),
]

DEFAULT_FROM_EMAIL = 'noreply@localhost'
FROM_EMAIL_WITH_SLUG = 'noreply+{slug}@localhost'
ANSWERABLE_FROM_EMAIL = 'noreply@localhost'
DEFAULT_REPLY_TO_EMAIL = 'reply+{reply_key}@localhost'
STADTGESTALTEN_BOT_EMAIL = 'grouprise-bot@localhost'

SERVER_EMAIL = 'grouprise <noreply@localhost>'
GROUPRISE_POSTMASTER_EMAIL = 'postmaster@localhost'


OPERATOR_GROUP_ID = 1
STADTGESTALTEN_FEEDS_IMPORTER_USER_ID = 1
GROUPRISE_FEEDS_IMPORTER_GESTALT_ID = 1
GROUPRISE_UNKNOWN_GESTALT_ID = 1
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# ENTITY_SLUG_BLACKLIST = [ 'all', 'alle', 'antwort', 'crew', 'facebook', 'gbr', 'info', 'kontakt', 'mail', 'noreply', 'postmaster', 'presse', 'reply', 'stadt', 'unknown', 'webmaster', 'www']

# set debug mode to false
DEBUG = False

# increase session cookie time to 1 year
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365


STADTGESTALTEN_CLAIMS = [
    'your claim 1',
    'your claim 2',
    # ...
]

# HAYSTACK_CONNECTIONS['default']['PATH'] = os.path.join(DATA_DIR, 'xapian_index')
