import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


# Django Basics
# https://docs.djangoproject.com/en/stable/

INSTALLED_APPS = [
    # grouprise features
    'features.articles',
    'features.associations',
    'features.contributions',
    'features.conversations',
    'features.content',
    'features.events',
    'features.files',
    'features.galleries',
    'features.gestalten',
    'features.gestalten.auth',
    'features.groups',
    'features.images',
    'features.imports',
    'features.memberships',
    'features.polls',
    'features.sharing',
    'features.stadt',
    'features.subscriptions',
    'features.tags',

    # grouprise core
    'core',

    # third-party packages
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'django_filters',
    'django_mailbox',
    'huey.contrib.djhuey',
    'haystack',
    'imagekit',
    'rest_framework',
    'rules',

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
    # django
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # django contrib
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # django-csp
    'csp.middleware.CSPMiddleware',
    # grouprise
    'features.gestalten.middleware.GestaltAppConfigMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'builtins': ['core.templatetags.core'],
            'context_processors': [
                # django core
                'django.template.context_processors.request',
                # django contrib
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # grouprise core
                'core.context_processors.settings',
                # grouprise features
                'features.groups.context_processors.groups',
                'features.stadt.context_processors.page_meta',
            ],
        },
    },
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

ROOT_URLCONF = 'stadt.urls'

WSGI_APPLICATION = 'stadt.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


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

ACCOUNT_ADAPTER = 'features.gestalten.adapters.AccountAdapter'

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_SUBJECT_PREFIX = ''

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_PRESERVE_USERNAME_CASING = False

ACCOUNT_USER_DISPLAY = lambda u: u.gestalt    # noqa: E731

ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_USERNAME_VALIDATORS = 'features.gestalten.forms.username_validators'


# Haystack
# https://django-haystack.readthedocs.io/

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'xapian_backend.XapianEngine',
        'PATH': os.path.join(BASE_DIR, 'xapian_index'),
    },
}

HAYSTACK_XAPIAN_LANGUAGE = 'german2'


# Django Rest Framework
# http://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'core.permissions.RulesPermissions',
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
}


# Django-CSP
# https://django-csp.readthedocs.io/

# sha256-Tli: allow the inline script defined in core/templates/core/base.html
CSP_SCRIPT_SRC = ("'self'", "'sha256-TliXkWbZj93MFmAkxUonwpWsbHfZT4sGVDOblkOGFQg='")

CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")


# grouprise Tags (features.tags)

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
