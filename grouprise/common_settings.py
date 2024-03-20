import os

import allauth

# This mechanism should be used for all settings, which depend on other settings.
# The callable should expect a single argument: a dictionary containing the django settings
# (previsely: `locals()` in the current context).
from .settings_utils import grouprise_field_resolver


GROUPRISE_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
# overridden by the `data_path` configuration setting (if present)
# You may *never* refer to `GROUPRISE_DATA_DIR` directly within this module, since it
# depends on the (later) resolving of configuration settings.
# Thus, you always need to use the `grouprise_field_resolver` approach described below.
GROUPRISE_DATA_DIR = os.path.dirname(GROUPRISE_PACKAGE_DIR)


# Django Basics
# https://docs.djangoproject.com/en/stable/

INSTALLED_APPS = [
    # grouprise features
    "grouprise.features.articles",
    "grouprise.features.associations",
    "grouprise.features.builtin_inbox_notifications",
    "grouprise.features.contributions",
    "grouprise.features.conversations",
    "grouprise.features.content",
    "grouprise.features.email_notifications",
    "grouprise.features.events",
    "grouprise.features.files",
    "grouprise.features.galleries",
    "grouprise.features.gestalten",
    "grouprise.features.gestalten.auth",
    "grouprise.features.groups",
    "grouprise.features.images",
    "grouprise.features.imports",
    "grouprise.features.memberships",
    "grouprise.features.notifications",
    "grouprise.features.polls",
    "grouprise.features.stadt",
    "grouprise.features.subscriptions",
    "grouprise.features.tags",
    # grouprise core
    "grouprise.core",
    # third-party packages
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "cachalot",
    "django_filters",
    "huey.contrib.djhuey",
    "haystack",
    "imagekit",
    "rest_framework",
    "rules",
    "taggit",
    # contributed django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.redirects",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    # basic django apps
    "django.forms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    # grouprise
    "grouprise.features.geo.middleware.GeoAppConfigMiddleware",
    "grouprise.features.gestalten.middleware.GestaltAppConfigMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
]

# allauth introduced its middleware requirement in v0.56.0
if allauth.VERSION >= (0, 56):
    MIDDLEWARE += ["allauth.account.middleware.AccountMiddleware"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        # keep this, even if empty so local settings can easily append
        "DIRS": [],
        "OPTIONS": {
            "builtins": [
                "grouprise.core.templatetags.defaultfilters",
                "grouprise.core.templatetags.defaulttags",
                "grouprise.features.tags.templatetags.defaulttags",
                "rules.templatetags.rules",
            ],
            "context_processors": [
                # django core
                "django.template.context_processors.request",
                # django contrib
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # grouprise core
                "grouprise.core.context_processors.settings",
                # grouprise features
                "grouprise.features.groups.context_processors.groups",
                "grouprise.features.stadt.context_processors.page_meta",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

ROOT_URLCONF = "grouprise.urls"

WSGI_APPLICATION = "grouprise.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(GROUPRISE_PACKAGE_DIR, "locale")]


# Sites
# https://docs.djangoproject.com/en/stable/ref/contrib/sites/

SITE_ID = 1


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = "/stadt/static/"

STATIC_ROOT = grouprise_field_resolver.get_resolver(
    ("STATIC_ROOT",),
    lambda settings_dict: os.path.join(settings_dict["GROUPRISE_DATA_DIR"], "static"),
)


# Media files (User uploaded files)
# https://docs.djangoproject.com/en/stable/topics/files/

MEDIA_URL = "/stadt/media/"

MEDIA_ROOT = grouprise_field_resolver.get_resolver(
    ("MEDIA_ROOT",),
    lambda settings_dict: os.path.join(settings_dict["GROUPRISE_DATA_DIR"], "media"),
)

FILE_UPLOAD_PERMISSIONS = 0o644


# Authentication backends
# https://docs.djangoproject.com/en/stable/topics/auth/customizing/#authentication-backends

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "rules.permissions.ObjectPermissionBackend",
]


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation"
        ".UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation" ".NumericPasswordValidator",
    },
]


# Authentication
# http://django-allauth.readthedocs.org/

LOGIN_URL = "account_login"

LOGIN_REDIRECT_URL = "index"

ACCOUNT_ADAPTER = "grouprise.features.gestalten.adapters.AccountAdapter"

ACCOUNT_AUTHENTICATION_METHOD = "username_email"

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_SUBJECT_PREFIX = ""

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_PRESERVE_USERNAME_CASING = False

ACCOUNT_USER_DISPLAY = lambda u: u.gestalt  # noqa: E731

ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_USERNAME_VALIDATORS = "grouprise.features.gestalten.forms.username_validators"

# Haystack
# https://django-haystack.readthedocs.io/

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "xapian_backend.XapianEngine",
        "PATH": grouprise_field_resolver.get_resolver(
            ("HAYSTACK_CONNECTIONS", "default", "PATH"),
            lambda settings_dict: os.path.join(
                settings_dict["GROUPRISE_DATA_DIR"], "xapian_index"
            ),
        ),
    },
}


# Django Rest Framework
# http://www.django-rest-framework.org/

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("grouprise.core.permissions.RulesPermissions",),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "VIEW_DESCRIPTION_FUNCTION": "grouprise.features.rest_api.views.get_view_description",
}


# Django-CSP
# https://django-csp.readthedocs.io/

# sha256-Tli: allow the inline script defined in core/templates/core/base.html
CSP_DEFAULT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'sha256-TliXkWbZj93MFmAkxUonwpWsbHfZT4sGVDOblkOGFQg='")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")


# grouprise Score Processors

GROUPRISE_SCORE_PROCESSORS = (
    "grouprise.features.stadt.scores.Gestalt",
    "grouprise.features.stadt.scores.Group",
)


# grouprise Repeatable Tasks (grouprise.core)

GROUPRISE_REPEATABLE_TASKS = {
    "content2.Content": (
        "grouprise.features.email_notifications.tasks.send_content_notifications"
    ),
    "contributions.Contribution": (
        "grouprise.features.email_notifications.tasks.send_contribution_notifications"
    ),
}


# django-taggit
# https://django-taggit.readthedocs.io/

TAGGIT_CASE_INSENSITIVE = True


# grouprise Tags (grouprise.features.tags)

GROUPRISE_TAGS_TAGGABLE = (
    {
        "entity": "content2.Content",
        "props": ["title"],
        "tag_self": True,
    },
    {
        "entity": "content2.Version",
        "props": ["text"],
        "tag_related": [lambda v: v.content],
    },
    {
        "entity": "contributions.Contribution",
        "props": ["contribution__text"],
        "tag_related": [lambda c: c.container],
        "constraint": lambda c: (
            not c.container.is_conversation and hasattr(c.contribution, "text")
        ),
    },
)
