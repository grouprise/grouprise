import copy
import functools
import os
import tempfile
from unittest import TestCase

import ruamel.yaml

from .settings_loader import ConfigError, import_settings_from_dict

DEFAULT_SLUG_DENYLIST = (
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
)

# default incoming configuration for tests
CONFIG_EXAMPLE = ruamel.yaml.YAML().load(
    """
backup_path: /tmp
branding:
        logo_backdrop: /logo/backdrop.png
        logo_favicon: /logo/favicon.png
        logo_square: /logo/square.png
        logo_text: /logo/text.png
        theme_color: "#123456"
claims:
        - "Communities collaborate!"
        - "Local is key"
collector_mailbox_address: collector@example.net
csp:
        connect_src:
                - "https://tracker.example.net"
        default_src:
                - "https://tracker.example.org"
        script_src:
                - "https://tracker.example.net"
                - "'sha256-J/TOUvP2iy3vYT4YNCGNCxigNR11I1/Zt517suNX1hk='"
debug: false
default_distinct_from_email: sender-{slug}@example.net
default_from_email: sender@example.net
default_reply_to_email: sender-{reply_key}@example.net
domain: example.net
entity_slug_blacklist:
        - local
email_submission:
        backend: dummy
        encryption: starttls
        host: mail
        user: foo
        password: bar
extra_allowed_hosts:
        - www.example.net
feed_importer_gestalt_id: 23
hook_script_paths:
        - /usr/local/bin/foo
language_code: en-us
log_recipient_emails:
        - admin@example.org
mailinglist_enabled: false
matrix_chat:
        enabled: true
        domain: example.org
        admin_api_url: http://localhost:8008/api
        bot_username: bot-example
        bot_access_token: 0123456789abcdef
media_root: /tmp
operator_group_id: 42
postmaster_email: postmaster@example.org
oidc_provider:
        enabled: true
score_content_age: 12
scripts:
        - path: /foo.js
          load: blocking
        - path: /bar.js
        - content: 'alert("hello");'
secret_key: "very-secret-django-key"
session_cookie_age: 1000
stylesheets:
        - path: /custom.css
        - path: /print.css
          media: print
template_directories:
        - /run
time_zone: Europe/Berlin
transport_security: disabled
unknown_gestalt_id: 61
upload_max_file_size: 1024
"""
)

DJANGO_SETTINGS_MINIMAL = {
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL": "https",
    "ALLOWED_HOSTS": ["example.org"],
    "CSRF_COOKIE_SECURE": True,
    "CACHES": {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.expanduser("~/grouprise.sqlite3"),
        }
    },
    "DEFAULT_FROM_EMAIL": "noreply@example.org",
    "EMAIL_PORT": 25,
    "EMAIL_USE_SSL": False,
    "EMAIL_USE_TLS": False,
    "HAYSTACK_XAPIAN_LANGUAGE": "german2",
    "LANGUAGE_CODE": "de-de",
    "SECURE_HSTS_SECONDS": 31536000,
    "SECURE_PROXY_SSL_HEADER": ("HTTP_X_FORWARDED_PROTO", "https"),
    "SECURE_SSL_REDIRECT": True,
    "SERVER_EMAIL": "noreply@example.org",
    "SESSION_COOKIE_SECURE": True,
    "TEMPLATES": [{"DIRS": []}],
    "TIME_ZONE": "Europe/Berlin",
}

# the following settings results from the above CONFIG_EXAMPLE
DJANGO_SETTINGS_EXAMPLE = {
    "ACCOUNT_DEFAULT_HTTP_PROTOCOL": "http",
    "ADMINS": [("", "admin@example.org")],
    "ALLOWED_HOSTS": ["example.net", "www.example.net"],
    "CACHES": {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    "CSP_CONNECT_SRC": ["https://tracker.example.net"],
    "CSP_DEFAULT_SRC": ["https://tracker.example.org"],
    "CSP_SCRIPT_SRC": [
        "https://tracker.example.net",
        "'sha256-J/TOUvP2iy3vYT4YNCGNCxigNR11I1/Zt517suNX1hk='",
        "'sha384-TirQsvnG1MeGfZkhq8L6lMDkgOou3m57SpmscoAaKeSlZ42p1PWjQWD5Hsvyra7f'",
    ],
    "DATABASES": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.expanduser("~/grouprise.sqlite3"),
        }
    },
    "DEBUG": False,
    "DEFAULT_FROM_EMAIL": "sender@example.net",
    "EMAIL_BACKEND": "django.core.mail.backends.dummy.EmailBackend",
    "EMAIL_HOST": "mail",
    "EMAIL_HOST_USER": "foo",
    "EMAIL_HOST_PASSWORD": "bar",
    "EMAIL_PORT": 587,
    "EMAIL_USE_SSL": False,
    "EMAIL_USE_TLS": True,
    "GROUPRISE": {
        "BACKUP_PATH": "/tmp",
        "BRANDING_LOGO_BACKDROP": "/logo/backdrop.png",
        "BRANDING_LOGO_FAVICON": "/logo/favicon.png",
        "BRANDING_LOGO_SQUARE": "/logo/square.png",
        "BRANDING_LOGO_TEXT": "/logo/text.png",
        "BRANDING_THEME_COLOR": "#123456",
        "CLAIMS": ["Communities collaborate!", "Local is key"],
        "COLLECTOR_MAILBOX_ADDRESS": "collector@example.net",
        "DEFAULT_DISTINCT_FROM_EMAIL": "sender-{slug}@example.net",
        "DEFAULT_REPLY_TO_EMAIL": "sender-{reply_key}@example.net",
        "ENTITY_SLUG_BLACKLIST": DEFAULT_SLUG_DENYLIST + ("local",),
        "FEED_IMPORTER_GESTALT_ID": 23,
        "HEADER_ITEMS": [
            '<link rel="stylesheet" href="/custom.css">',
            '<link rel="stylesheet" href="/print.css" media="print">',
            '<script src="/foo.js" />',
            '<script src="/bar.js" async defer />',
            '<script type="application/javascript">alert("hello");</script>',
        ],
        "HOOK_SCRIPT_PATHS": ["/usr/local/bin/foo"],
        "MAILINGLIST_ENABLED": False,
        "MATRIX_CHAT": {
            "ADMIN_API_URL": "http://localhost:8008/api",
            "BOT_ACCESS_TOKEN": "0123456789abcdef",
            "BOT_USERNAME": "bot-example",
            "DOMAIN": "example.org",
            "ENABLED": True,
        },
        "OPERATOR_GROUP_ID": 42,
        "POSTMASTER_EMAIL": "postmaster@example.org",
        "SCORE_CONTENT_AGE": 12,
        "UNKNOWN_GESTALT_ID": 61,
        "UPLOAD_MAX_FILE_SIZE": 1024,
    },
    "HAYSTACK_XAPIAN_LANGUAGE": "english",
    "INSTALLED_APPS": [
        "grouprise.features.matrix_chat",
        "corsheaders",
        "oauth2_provider",
    ],
    "LANGUAGE_CODE": "en-us",
    "MEDIA_ROOT": "/tmp",
    "MIDDLEWARE": ["corsheaders.middleware.CorsMiddleware"],
    "OAUTH2_PROVIDER": {
        "OAUTH2_VALIDATOR_CLASS": "grouprise.auth.oauth_validators.AccountOAuth2Validator",
        "OIDC_ENABLED": True,
        "OIDC_RSA_PRIVATE_KEY": "secret-key-content",
        "SCOPES": {"openid": "OpenID Connect scope"},
    },
    "SECRET_KEY": "very-secret-django-key",
    "SERVER_EMAIL": "sender@example.net",
    "SESSION_COOKIE_AGE": 1000,
    "TEMPLATES": [{"DIRS": ["/run"]}],
    "TIME_ZONE": "Europe/Berlin",
}


def get_modified_dict(baseset, remove_keys=None, **kwargs):
    """copy an existing dictionary and add, remove or modify keys

    This is helpful for using modified templates after applying changes.
    """
    result = copy.deepcopy(baseset)
    for key in remove_keys or []:
        del result[key]
    result.update(**kwargs)
    return result


class ContentFile:
    """generate a content file on demand"""

    def __init__(self, path, mode=None, content=None):
        self._path = path
        self._mode = mode
        self._content = content

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(test_class, *args, **kwargs):
            file_path = os.path.join(test_class.temporary_directory, self._path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as out_file:
                if self._content:
                    out_file.write(self._content)
            if self._mode:
                os.chmod(file_path, self._mode)
            try:
                result = func(test_class, *args, **kwargs)
            finally:
                os.remove(file_path)
            return result

        return wrapped


class SettingsLoaderTest(TestCase):

    # tolerate hugh diffs of dictionaries
    maxDiff = None

    def setUp(self):
        self.temporary_directory = tempfile.mkdtemp()

    def tearDown(self):
        os.rmdir(self.temporary_directory)

    @ContentFile("oidc.key", content="secret-key-content")
    def test_all_settings(self):
        target = {}
        import_settings_from_dict(
            target, CONFIG_EXAMPLE, base_directory=self.temporary_directory
        )
        self.assertEqual(DJANGO_SETTINGS_EXAMPLE, target)

    def test_minimal_settings(self):
        target = {}
        import_settings_from_dict(target, {})
        self.assertEqual(DJANGO_SETTINGS_MINIMAL, target)

    def test_list_append(self):
        """verify that items can be added to existing lists"""
        stylesheet_pattern = '<link rel="stylesheet" href="/{}">'
        target = {"GROUPRISE": {"HEADER_ITEMS": [stylesheet_pattern.format("foo")]}}
        import_settings_from_dict(target, {"stylesheets": [{"path": "/bar"}]})
        wanted_result = copy.deepcopy(DJANGO_SETTINGS_MINIMAL)
        wanted_result.setdefault("GROUPRISE", {})
        wanted_result["GROUPRISE"]["HEADER_ITEMS"] = [
            stylesheet_pattern.format("foo"),
            stylesheet_pattern.format("bar"),
        ]
        self.assertEqual(wanted_result, target)

    def test_invalid_structure(self):
        """test various bad configuration input values"""
        for label, input_data in (
            ("Mismatched regular expression", {"domain": "foo*"}),
            ("Missing directory", {"media_root": "/nonexistent"}),
            ("Invalid database engine", {"database": {"engine": "invalid"}}),
            ("Invalid transport security", {"transport_security": "invalid"}),
            ("Invalid language code", {"language_code": "foo-bar-baz"}),
            ("Invalid email backend", {"email_submission": {"backend": "foo"}}),
            ("Invalid email encryption", {"email_submission": {"encryption": "foo"}}),
            ("Invalid stylesheet (key)", {"stylesheets": [{"no-path": "/foo"}]}),
            ("Invalid stylesheet (mistyped path)", {"stylesheets": [{"path": 3}]}),
            (
                "Invalid stylesheet (mistyped media)",
                {"stylesheets": [{"path": "/foo", "media": 4}]},
            ),
            ("Invalid scripts (key)", {"stylesheets": [{"no-path": "/foo"}]}),
            ("Invalid scripts (mistyped path)", {"stylesheets": [{"path": 3}]}),
            (
                "Invalid scripts (mistyped load)",
                {"scripts": [{"path": "/foo", "load": 3}]},
            ),
            (
                "Invalid scripts (invalid load)",
                {"scripts": [{"path": "/foo", "load": "bar"}]},
            ),
            (
                "Invalid scripts (conflict)",
                {"scripts": [{"path": "/foo", "content": "bar"}]},
            ),
            (
                "Invalid scripts (content/load)",
                {"scripts": [{"content": "foo", "load": "bar"}]},
            ),
            ("Mistyped integer (str)", {"session_cookie_age": "foo"}),
            ("Mistyped integer (list)", {"session_cookie_age": [1]}),
            ("Mistyped integer (dict)", {"session_cookie_age": {"value": 1}}),
            ("Mistyped boolean", {"debug": "yes"}),
            ("Mistyped list (dict)", {"extra_allowed_hosts": {"foo"}}),
            ("Mistyped list (str)", {"extra_allowed_hosts": "foo"}),
            ("Mistyped list (int)", {"extra_allowed_hosts": 2}),
            ("Mistyped dict (int)", {"email_submission": 2}),
            ("Mistyped dict (str)", {"email_submission": "foo"}),
            ("Mistyped dict (list)", {"email_submission": ["foo"]}),
        ):
            with self.subTest(label=label):
                with self.assertRaises(ConfigError):
                    import_settings_from_dict({}, input_data)
