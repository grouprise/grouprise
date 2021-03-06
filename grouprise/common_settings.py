import os
import sys

GROUPRISE_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(GROUPRISE_PACKAGE_DIR)

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


# Django Basics
# https://docs.djangoproject.com/en/stable/

INSTALLED_APPS = [
    # grouprise features
    'grouprise.features.articles',
    'grouprise.features.associations',
    'grouprise.features.contributions',
    'grouprise.features.conversations',
    'grouprise.features.content',
    'grouprise.features.email_notifications',
    'grouprise.features.events',
    'grouprise.features.files',
    'grouprise.features.galleries',
    'grouprise.features.gestalten',
    'grouprise.features.gestalten.auth',
    'grouprise.features.groups',
    'grouprise.features.images',
    'grouprise.features.imports',
    'grouprise.features.memberships',
    'grouprise.features.polls',
    'grouprise.features.stadt',
    'grouprise.features.subscriptions',
    'grouprise.features.tags',

    # grouprise core
    'grouprise.core',

    # third-party packages
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # deactivated, see #662
    # 'cachalot',
    'django_filters',
    'huey.contrib.djhuey',
    'haystack',
    'imagekit',
    'rest_framework',
    'rules',
    'taggit',

    # contributed django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    # basic django apps
    'django.forms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
    # grouprise
    'grouprise.features.gestalten.middleware.GestaltAppConfigMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        # keep this, even if empty so local settings can easily append
        'DIRS': [],
        'OPTIONS': {
            'builtins': [
                'grouprise.core.templatetags.defaultfilters',
                'grouprise.core.templatetags.defaulttags',
                'rules.templatetags.rules',
            ],
            'context_processors': [
                # django core
                'django.template.context_processors.request',
                # django contrib
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # grouprise core
                'grouprise.core.context_processors.settings',
                # grouprise features
                'grouprise.features.associations.context_processors.activity',
                'grouprise.features.groups.context_processors.groups',
                'grouprise.features.stadt.context_processors.page_meta',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

ROOT_URLCONF = 'grouprise.urls'

WSGI_APPLICATION = 'grouprise.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(GROUPRISE_PACKAGE_DIR, "locale")]


# Sites
# https://docs.djangoproject.com/en/stable/ref/contrib/sites/

SITE_ID = 1


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = '/stadt/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Media files (User uploaded files)
# https://docs.djangoproject.com/en/stable/topics/files/

MEDIA_URL = '/stadt/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

FILE_UPLOAD_PERMISSIONS = 0o644


# Authentication backends
# https://docs.djangoproject.com/en/stable/topics/auth/customizing/#authentication-backends

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'rules.permissions.ObjectPermissionBackend',
]


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation'
            '.NumericPasswordValidator',
    },
]


# Authentication
# http://django-allauth.readthedocs.org/

LOGIN_URL = 'account_login'

LOGIN_REDIRECT_URL = 'index'

ACCOUNT_ADAPTER = 'grouprise.features.gestalten.adapters.AccountAdapter'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_PRESERVE_USERNAME_CASING = False

ACCOUNT_USER_DISPLAY = lambda u: u.gestalt    # noqa: E731

ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_USERNAME_VALIDATORS = 'grouprise.features.gestalten.forms.username_validators'

# Backports of upcoming Django setting default changes
# Some security related settings are changed for new versions of Django.  In some cases we want to
# use these new defaults before switching to the new version.
# These setting overrides can be removed as soon as grouprise requires a newer version of Django.
# New defaults introduced with Django 3.0:
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Haystack
# https://django-haystack.readthedocs.io/

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'xapian_backend.XapianEngine',
        'PATH': os.path.join(BASE_DIR, 'xapian_index'),
    },
}

HAYSTACK_XAPIAN_LANGUAGE = 'german2'


HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'filename': os.path.join(BASE_DIR, 'huey.sqlite'),
    # Do not store results of tasks, since we do not use them.
    # Otherwise we would need to run the following periodically:
    #   from huey.contrib.djhuey import HUEY
    #   HUEY.storage.flush_results()
    'results': False,
}


# Django Rest Framework
# http://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'grouprise.core.permissions.RulesPermissions',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'VIEW_DESCRIPTION_FUNCTION': 'grouprise.features.rest_api.views.get_view_description',
}


# Django-CSP
# https://django-csp.readthedocs.io/

# sha256-Tli: allow the inline script defined in core/templates/core/base.html
CSP_DEFAULT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'sha256-TliXkWbZj93MFmAkxUonwpWsbHfZT4sGVDOblkOGFQg='")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

# Sentry Configuration
SENTRY_DSN = None


# grouprise Score Processors

GROUPRISE_SCORE_PROCESSORS = (
    'grouprise.features.stadt.scores.Gestalt',
    'grouprise.features.stadt.scores.Group',
)


# grouprise Repeatable Tasks (grouprise.core)

GROUPRISE_REPEATABLE_TASKS = {
    'content2.Content':
    'grouprise.features.email_notifications.tasks.send_content_notifications',

    'contributions.Contribution':
    'grouprise.features.email_notifications.tasks.send_contribution_notifications',
}


# django-taggit
# https://django-taggit.readthedocs.io/

TAGGIT_CASE_INSENSITIVE = True


# grouprise Tags (grouprise.features.tags)

GROUPRISE_TAGS_TAGGABLE = (
    {
        'entity': 'content2.Content',
        'props': ['title'],
        'tag_self': True,
    },
    {
        'entity': 'content2.Version',
        'props': ['text'],
        'tag_related': [lambda v: v.content],
    },
    {
        'entity': 'contributions.Contribution',
        'props': ['contribution__text'],
        'tag_related': [lambda c: c.container],
        'constraint': lambda c: (not c.container.is_conversation
                                 and hasattr(c.contribution, 'text')),
    },
)
