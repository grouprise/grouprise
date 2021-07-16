from distutils.version import LooseVersion
import enum
import importlib.util
import logging
import os
import re
import types

import ruamel.yaml


logger = logging.getLogger(__name__)


CONFIGURATION_FILENAME_PATTERN = re.compile(r"^[\w-]+\.yaml$")
# django-oauth-toolkit introduced OIDC support in v1.5
# https://django-oauth-toolkit.readthedocs.io/en/1.5.0/changelog.html#id1
MINIMUM_OAUTH2_VERSION = "1.5.0"
# from user configuration name to the name used by django
DATABASE_ENGINES_MAP = {
    "mysql": "django.db.backends.mysql",
    "postgresql": "django.db.backends.postgresql",
    "sqlite": "django.db.backends.sqlite3",
}
EMAIL_BACKENDS_MAP = {
    "console": "django.core.mail.backends.console.EmailBackend",
    "dummy": "django.core.mail.backends.dummy.EmailBackend",
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
}


class EmailSubmissionEncryption(enum.Enum):
    PLAIN = "plain"
    STARTTLS = "starttls"
    SSL = "ssl"


def get_configuration_path_candidates():
    """return a list locations where grouprise configuration files may be looked for

    The resulting paths may not exist.
    """
    result = []
    for path in (
        os.getenv("GROUPRISE_CONFIG"),
        # development setup: grouprise.yaml in the current directory
        os.path.join(os.getcwd(), "grouprise.yaml"),
        os.path.expanduser("~/.config/grouprise/conf.d"),
        "/etc/grouprise/conf.d",
    ):
        if path:
            result.append(os.path.abspath(path))
    return result


def get_configuration_filenames(location_candidates=None):
    """determine suitable configuration files based on a list of location candidates

    If no "location_candidates" are given, the result of "get_configuration_path_candidates()" is
    used.
    The locations are tested in the given order.  The first candidate pointing at a file or
    pointing at a directory containing suitables files (alphanumeric characters or hyphen, with
    ".yaml" extension) is used.  All following candidates are discarded.
    A number of filenames (absolute paths) is returned.
    An empty list is returned, if no suitable files were found.
    """
    if location_candidates is None:
        location_candidates = get_configuration_path_candidates()
    result = []
    for path in location_candidates:
        if os.path.exists(path):
            if os.path.isdir(path):
                for filename in sorted(os.listdir(path)):
                    full_path = os.path.abspath(os.path.join(path, filename))
                    if os.path.isfile(
                        full_path
                    ) and CONFIGURATION_FILENAME_PATTERN.match(filename):
                        result.append(full_path)
            elif os.path.isfile(path):
                result.append(os.path.abspath(path))
            else:
                # skip any other kind of objects
                pass
        # stop testing further candidate locations as soon as the first configuration file is found
        if result:
            return result
    else:
        # no suitable configuration file was found
        return []


def load_settings_from_yaml_files(locations=None):
    config_filenames = get_configuration_filenames(location_candidates=locations)
    combined_configuration = {}
    loader = ruamel.yaml.YAML()
    for config_filename in config_filenames:
        with open(config_filename, "r") as config_file:
            data = loader.load(config_file)
            if data is None:
                pass
            elif not isinstance(data, dict):
                raise ConfigError(
                    f"Skipping configuration file '{config_filename}', since it does not contain "
                    f"a yaml dictionary at the top level.  Please ensure that the first line "
                    f"contains something like 'foo: bar' (instead of '- foo: bar')."
                )
            else:
                combined_configuration.update(data)
    return combined_configuration


class ConfigError(ValueError):
    """ any kind of configuration error """


class ConfigBase:

    DEFAULT = None

    def __init__(self, name=None, django_target=None, default=None):
        if (
            (default is not None)
            and django_target
            and not callable(django_target)
            and (django_target[0] == "GROUPRISE")
        ):
            logger.warning(
                f"Configuration handling: defaults for grouprise-specific settings "
                f"({django_target}) should always be defined in grouprise.*.settings "
                f"(not in {__name__})"
            )
        self.name = name
        # we do not use "self.default" directly - we just store it for the caller's convenience
        self.default = default
        self.django_target = django_target

    def validate(self, value):
        pass

    def apply_to_settings(self, settings, value):
        if isinstance(self.django_target, str):
            settings[self.django_target] = value
        elif isinstance(self.django_target, (list, tuple)):
            # traverse a path down a hierarchy of dictionaries
            current = settings
            # walk down the hierarchy (except for the last item)
            for item in self.django_target[:-1]:
                if item not in current:
                    current[item] = {}
                current = current[item]
            # assign the value (the last item in the target list)
            key = self.django_target[-1]
            current[key] = value
        elif callable(self.django_target):
            self.django_target(settings, value)
        else:
            raise ValueError(
                "Internal error: 'django_target' must be a string, a list of strings or a "
                f"callable: {type(self.django_target)} ('{self.django_target}')"
            )


class StringConfig(ConfigBase):
    def __init__(self, *args, regex=None, min_length=None, **kwargs):
        if regex and isinstance(regex, str):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        self.min_length = min_length
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, str):
            raise ConfigError(
                f"Setting '{self.name}' must be a string: {value} (type: {type(value)})"
            )
        if self.min_length:
            if len(value) < self.min_length:
                raise ConfigError(
                    f"Setting '{self.name}' is too short (less than {self.min_length} characters):"
                    f" {value}"
                )
        if self.regex:
            if not self.regex.match(value):
                raise ConfigError(
                    f"Setting '{self.name}' does not match the required regular expression"
                    f" ({self.regex.pattern}): {value}"
                )


class BooleanConfig(ConfigBase):
    def validate(self, value):
        super().validate(value)
        if not isinstance(value, bool):
            raise ConfigError(
                f"Setting '{self.name}' must be a boolean value: {value} (type: {type(value)})"
            )


class IntegerConfig(ConfigBase):
    def __init__(self, *args, minimum=None, maximum=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, int):
            raise ConfigError(
                f"Setting '{self.name}' must be an integer value: {value} (type: {type(value)})"
            )
        if (self.minimum is not None) and (value < self.minimum):
            raise ConfigError(
                f"Setting '{self.name}' is too small (less than {self.minimum}: {value}"
            )
        if (self.maximum is not None) and (value > self.maximum):
            raise ConfigError(
                f"Setting '{self.name}' is too big (greater than {self.maximum}: {value}"
            )


class ChoicesConfig(ConfigBase):
    def __init__(self, *args, choices=None, **kwargs):
        self.choices = choices
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if value not in self.choices:
            raise ConfigError(
                f"Setting '{self.name}' must be one of {self.choices}: {value}"
            )


class ListConfig(ConfigBase):
    def __init__(self, *args, append=None, append_pre_default=None, **kwargs):
        self.append = append
        # for "append" operations: fill the list with the given values, before appending new ones
        self.append_pre_default = append_pre_default
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, list):
            raise ConfigError(
                f"Setting '{self.name}' must be a list: {value} (type: {type(value)})"
            )

    def apply_to_settings(self, settings, value):
        if self.append:
            # normalize the target to a list
            if isinstance(self.django_target, (list, tuple)):
                path = self.django_target
            else:
                path = [self.django_target]
            # Do not apply the concatenation ("+=") directly to the value, but reference it via its
            # parent.  Otherwise concatenation would have no effect on tuples.
            parent = _get_nested_dict_value(settings, path[:-1], default={})
            parent.setdefault(path[-1], self.append_pre_default or [])
            parent[path[-1]] += tuple(value)
        else:
            super().apply_to_settings(settings, value)


class DatabaseConfig(ConfigBase):

    DEFAULT_ENGINE = "sqlite"

    def validate(self, value):
        super().validate(value)
        if not value.get("engine", self.DEFAULT_ENGINE) in DATABASE_ENGINES_MAP:
            raise ConfigError(
                f"Invalid database engine: '{value['engine']}' "
                f"(supported: {DATABASE_ENGINES_MAP.keys()})"
            )

    def apply_to_settings(self, settings, value):
        dest = {}
        for in_key, out_key in (
            ("host", "HOST"),
            ("port", "PORT"),
            ("name", "NAME"),
            ("user", "USER"),
            ("password", "PASSWORD"),
        ):
            if in_key in value:
                dest[out_key] = value[in_key]
        dest["ENGINE"] = DATABASE_ENGINES_MAP[value.get("engine", self.DEFAULT_ENGINE)]
        settings["DATABASES"] = {"default": dest}


class EmailBackendConfig(ChoicesConfig):
    def apply_to_settings(self, settings, value):
        settings["EMAIL_BACKEND"] = EMAIL_BACKENDS_MAP[value]


class EmailSubmissionEncryptionConfig(ChoicesConfig):
    def apply_to_settings(self, settings, value):
        value = EmailSubmissionEncryption(value)
        use_tls = False
        use_ssl = False
        if value is EmailSubmissionEncryption.PLAIN:
            port = 25
        elif value is EmailSubmissionEncryption.SSL:
            use_ssl = True
            port = 465
        elif value is EmailSubmissionEncryption.STARTTLS:
            use_tls = True
            port = 587
        else:
            raise ValueError(
                f"Internal error: 'email_submission.encryption' contains an invalid value: {value}"
            )
        settings["EMAIL_USE_TLS"] = use_tls
        settings["EMAIL_USE_SSL"] = use_ssl
        settings["EMAIL_PORT"] = port


class DirectoryConfig(StringConfig):
    def validate(self, value):
        super().validate(value)
        if not os.path.exists(value):
            raise ConfigError(
                f"The configured directory ({self.name}={value}) does not exist"
            )
        if not os.path.isdir(value):
            raise ConfigError(
                f"The configured path ({self.name}={value}) is not a directory"
            )

    def apply_to_settings(self, settings, value):
        """ store an absolute path in the configuration """
        abspath = os.path.abspath(value)
        super().apply_to_settings(settings, abspath)


class WritableDirectoryConfig(DirectoryConfig):
    def validate(self, value):
        super().validate(value)
        if not os.access(value, os.W_OK):
            raise ConfigError(
                f"The configured directory ({self.name}={value}) is not writable"
            )


class ReadableFileConfig(StringConfig):
    def validate(self, value):
        super().validate(value)
        if not os.path.exists(value):
            raise ConfigError(
                f"The configured file ({self.name}={value}) does not exist"
            )
        if not os.path.isfile(value):
            raise ConfigError(
                f"The configured path ({self.name}={value}) is not a file"
            )
        if not os.access(value, os.R_OK):
            raise ConfigError(
                f"The configured file ({self.name}={value}) is not readable"
            )


class LanguageCodeConfig(StringConfig):

    # source: https://xapian.org/docs/apidoc/html/classXapian_1_1Stem.html
    XAPIAN_LANGUAGE_MAP = {
        "ar": "arabic",
        "ca": "catalan",
        "da": "danish",
        "de": "german2",
        "en": "english",
        "es": "spanish",
        "eu": "basque",
        "nl": "dutch",
        "fi": "finnish",
        "fr": "french",
        "ga": "irish",
        "hu": "hungarian",
        "hy": "armenian",
        "id": "indonesian",
        "it": "italian",
        "lt": "lithuanian",
        "nb": "norwegian",
        "ne": "nepali",
        "nn": "norwegian",
        "no": "norwegian",
        "pt": "portuguese",
        "ro": "romanian",
        "ru": "russian",
        "sv": "swedish",
        "ta": "tamil",
        "tr": "turkish",
    }

    def apply_to_settings(self, settings, value):
        settings["LANGUAGE_CODE"] = value
        primary_tag = value.lower().replace("_", "-").split("-")[0]
        xapian_language = self.XAPIAN_LANGUAGE_MAP.get(primary_tag, self.default)
        if xapian_language:
            settings["HAYSTACK_XAPIAN_LANGUAGE"] = xapian_language


class TransportSecurityConfig(ChoicesConfig):

    # integrated: a django app is used for providing SSL encryption (e.g. "sslserver")
    # reverse-proxy: a reverse proxy is providing transport layer security
    # disabled: the site is published via http-only
    choices = {"integrated", "reverse-proxy", "disabled"}

    def apply_to_settings(self, settings, value):
        if value in {"integrated", "reverse-proxy"}:
            settings["SECURE_HSTS_SECONDS"] = 365 * 24 * 3600
            settings["SESSION_COOKIE_SECURE"] = True
            settings["CSRF_COOKIE_SECURE"] = True
            settings["SECURE_SSL_REDIRECT"] = True
            settings["ACCOUNT_DEFAULT_HTTP_PROTOCOL"] = "https"
        if value == "reverse-proxy":
            # it is reasonable to assume that this typical header is configured on the proxy
            settings["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")
        if value == "disabled":
            settings["ACCOUNT_DEFAULT_HTTP_PROTOCOL"] = "http"


class TemplateDirectoriesConfig(ListConfig):
    def validate(self, value):
        super().validate(value)
        for item in value:
            if not os.path.exists(item):
                raise ConfigError(
                    f"Failed to find configured templates directory: {item}"
                )
            if not os.path.isdir(item):
                raise ConfigError(
                    f"Configured template location is not a directory: {item}"
                )

    def apply_to_settings(self, settings, value):
        # create a dummy "TEMPLATES" attribute, if it is missing (useful only for tests)
        templates = _get_nested_dict_value(settings, ["TEMPLATES"], [])
        if not templates:
            templates.append({"DIRS": []})
        templates[0]["DIRS"].extend(os.path.abspath(path) for path in value)


class AdministratorEmailsConfig(ListConfig):
    def validate(self, value):
        super().validate(value)
        for item in value:
            if not re.match(r"[\w\-.@]*$", item):
                raise ConfigError(f"Malformed email address in '{self.name}': {item}")

    def apply_to_settings(self, settings, value):
        settings["ADMINS"] = [("", item) for item in value]


class MatrixAppEnableConfig(BooleanConfig):
    def apply_to_settings(self, settings, value):
        # store the boolean value
        super().apply_to_settings(settings, value)
        # enable the matrix_chat django application
        apps = _get_nested_dict_value(settings, ["INSTALLED_APPS"], [])
        apps.append("grouprise.features.matrix_chat")


class OIDCProviderEnableConfig(BooleanConfig):
    def __init__(self, *args, config_base_directory=None, **kwargs):
        self.config_base_directory = config_base_directory
        super().__init__(*args, **kwargs)

    def apply_to_settings(self, settings, value):
        # store the boolean value
        super().apply_to_settings(settings, value)
        if value:
            # enable the required applications and middleware
            apps = _get_nested_dict_value(settings, ["INSTALLED_APPS"], [])
            middleware = _get_nested_dict_value(settings, ["MIDDLEWARE"], [])
            provider = _get_nested_dict_value(settings, ["OAUTH2_PROVIDER"], {})
            apps.append("corsheaders")
            apps.append("oauth2_provider")
            middleware.insert(0, "corsheaders.middleware.CorsMiddleware")
            provider["OIDC_ENABLED"] = True
            provider.setdefault("SCOPES", {}).update({"openid": "OpenID Connect scope"})
            validator = "grouprise.auth.oauth_validators.AccountOAuth2Validator"
            provider["OAUTH2_VALIDATOR_CLASS"] = validator
            # verify the version of oauth2_provider (OIDC support started in v1.5.0)
            try:
                import oauth2_provider
            except ImportError:
                raise ConfigError(
                    "Failed to import 'oauth2_provider'. "
                    "The module is required for the OIDC provider, but it seems to be missing. "
                    "You should either disable OIDC ('oidc_provider: { enabled: false }') or "
                    "install the 'python3-django-oauth-toolkit' package (system-wide) or install "
                    "the 'django-oauth-toolkit' package via pip in a virtualenv."
                )
            installed_version = LooseVersion(oauth2_provider.__version__)
            wanted_version = LooseVersion(MINIMUM_OAUTH2_VERSION)
            if wanted_version < installed_version:
                raise ConfigError(
                    "The minimum required version of 'oauth2_provider' for OIDC support is "
                    f"{MINIMUM_OAUTH2_VERSION}. "
                    f"The installed version is only {oauth2_provider.__version__}. "
                    "You should either disable OIDC ('oidc_provider: { enabled: false }') or "
                    "install a newer version of the 'python3-django-oauth-toolkit package "
                    "(if available) or install the 'django-oauth-toolkit' package via pip in a "
                    "virtualenv."
                )
            # verify the availability of the "corsheaders" package
            try:
                import corsheaders  # noqa: F401
            except ImportError:
                raise ConfigError(
                    "The python package 'django-cors-headers' is missing. "
                    "This package is required for the OIDC provider."
                )
            if self.config_base_directory is None:
                raise ConfigError(
                    "OIDC is enabled, but the configuration's location could not be determined. "
                    "Thus the location of the OIDC key file cannot be defined."
                )
            oidc_key_filename = os.path.join(self.config_base_directory, "oidc.key")
            if not os.path.exists(oidc_key_filename):
                raise ConfigError(
                    f"Missing OIDC key file ({oidc_key_filename})."
                    f" You can create it via 'openssl genrsa -out ${oidc_key_filename} 4096'."
                )
            try:
                with open(oidc_key_filename, "r") as key_file:
                    oidc_key = key_file.read()
            except IOError as exc:
                raise ConfigError(
                    f"Failed to read OIDC key file ({oidc_key_filename}): {exc}"
                )
            settings["OAUTH2_PROVIDER"]["OIDC_RSA_PRIVATE_KEY"] = oidc_key


def _get_nested_dict_value(data, path, default=None):
    if isinstance(path, str):
        return data.get(path, default)
    elif not isinstance(data, dict):
        raise KeyError(f"Container is not a dictionary: {data}")
    elif len(path) == 0:
        return data
    elif len(path) == 1:
        return data.setdefault(path[0], default)
    else:
        return _get_nested_dict_value(data.get(path[0], {}), path[1:])


def recursivly_normalize_dict_keys_to_lower_case(data):
    """ walk through the data (through dicts and lists) and change all dict keys to lower case """
    if isinstance(data, dict):
        return {
            key.lower(): recursivly_normalize_dict_keys_to_lower_case(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [recursivly_normalize_dict_keys_to_lower_case(item) for item in data]
    else:
        return data


def get_config_base_directory(locations=None):
    """Try to determine, which directory could be regarded as the base configuration directory.

    The given locations (or being absent: the default locations) are scanned for configuration
    files.
    The directory of the first configuration file is returned (with a possibly trailing "conf.d"
    path component removed).  If no configuration files are found, None is returned.
    """
    config_directories = [
        os.path.dirname(filename)
        for filename in get_configuration_filenames(location_candidates=locations)
    ]
    if config_directories:
        # remove a trailing "conf.d" path component
        result = config_directories[0]
        if os.path.basename(result) == "conf.d":
            result = os.path.dirname(result)
        return result
    else:
        return None


def import_settings_from_yaml(settings, locations=None):
    """import grouprise settings from one or more yaml-formatted setting files

    The setting filenames are discovered based on the given list of suggested location candidates.
    The settings are merged in a trivial fashion: later configuration settings override existing
    settings with the same name.

    The special configuration directive "extra_django_settings_filenames" may contain a list of
    filenames, that will be loaded as python modules.
    See "import_settings_from_python" for details.
    """
    config = load_settings_from_yaml_files(locations)
    base_directory = get_config_base_directory(locations)
    return import_settings_from_dict(settings, config, base_directory=base_directory)


def import_settings_from_dict(settings: dict, config: dict, base_directory=None):
    """
    settings: the target dictionary to be populated (e.g. "locals()" in settings.py)
    config: the source dictionary parsed from a grouprise configuration file
    """
    # We want to tolerate settings with with upper-case instead of lower-case keys.
    # This should simplify the migration from Django-based settings to the yaml-based settings.
    config = recursivly_normalize_dict_keys_to_lower_case(config)
    default_domain = "example.org"
    configured_domain = config.get("domain", default_domain)
    parsers = [
        StringConfig(
            # TODO: festlegen, ob Datenbank oder Konfiguration die authorative Quelle sein soll
            name="domain",
            django_target=lambda settings, value: settings.update(
                {"ALLOWED_HOSTS": [value]}
            ),
            default=default_domain,
            regex=r"^[\w\-.]+$",
        ),
        WritableDirectoryConfig(name="media_root", django_target="MEDIA_ROOT"),
        DatabaseConfig(
            name="database",
            default={
                "engine": "sqlite",
                "name": os.path.expanduser("~/grouprise.sqlite3"),
            },
        ),
        IntegerConfig(
            name="session_cookie_age", django_target="SESSION_COOKIE_AGE", minimum=0
        ),
        TransportSecurityConfig(
            name="transport_security",
            choices={"disabled", "reverse-proxy", "integrated"},
            default="reverse-proxy",
        ),
        BooleanConfig(name="debug", django_target="DEBUG"),
        LanguageCodeConfig(
            name="language_code", default="de-de", regex=r"^\w+([-_]\w+)?$"
        ),
        StringConfig(name="time_zone", django_target="TIME_ZONE"),
        ListConfig(
            name="extra_allowed_hosts", django_target="ALLOWED_HOSTS", append=True
        ),
        EmailBackendConfig(
            name=("email_submission", "backend"), choices=EMAIL_BACKENDS_MAP.keys()
        ),
        # encryption needs to be applied *before* "EMAIL_PORT", since it selects a default port
        EmailSubmissionEncryptionConfig(
            name=("email_submission", "encryption"),
            choices={item.value for item in EmailSubmissionEncryption},
            default="plain",
        ),
        StringConfig(name=("email_submission", "host"), django_target="EMAIL_HOST"),
        IntegerConfig(
            name=("email_submission", "port"),
            django_target="EMAIL_PORT",
            minimum=1,
            maximum=65535,
        ),
        StringConfig(
            name=("email_submission", "user"), django_target="EMAIL_HOST_USER"
        ),
        StringConfig(
            name=("email_submission", "password"), django_target="EMAIL_HOST_PASSWORD"
        ),
        ListConfig(
            name=("csp", "script_src"), django_target="CSP_SCRIPT_SRC", append=True
        ),
        ListConfig(
            name=("csp", "default_src"), django_target="CSP_DEFAULT_SRC", append=True
        ),
        ListConfig(
            name=("csp", "connect_src"), django_target="CSP_CONNECT_SRC", append=True
        ),
        TemplateDirectoriesConfig(name="template_directories", default=[]),
        StringConfig(name="secret_key", django_target="SECRET_KEY", min_length=16),
        StringConfig(
            name="default_from_email",
            django_target=lambda settings, value: settings.update(
                {
                    "DEFAULT_FROM_EMAIL": value,
                    "SERVER_EMAIL": value,
                }
            ),
            default=f"noreply@{configured_domain}",
        ),
        StringConfig(
            name="default_distinct_from_email",
            django_target=("GROUPRISE", "DEFAULT_DISTINCT_FROM_EMAIL"),
            regex=r"^[^@]*\{slug\}[^@]*@.*",
        ),
        StringConfig(
            name="default_reply_to_email",
            django_target=("GROUPRISE", "DEFAULT_REPLY_TO_EMAIL"),
            regex=r"^[^@]*\{reply_key\}[^@]*@.*",
        ),
        StringConfig(
            name="collector_mailbox_address",
            django_target=("GROUPRISE", "COLLECTOR_MAILBOX_ADDRESS"),
            regex=r"^[^@]+@.*",
        ),
        StringConfig(
            name="postmaster_email",
            django_target=("GROUPRISE", "POSTMASTER_EMAIL"),
        ),
        BooleanConfig(
            name="mailinglist_enabled",
            django_target=("GROUPRISE", "MAILINGLIST_ENABLED"),
        ),
        StringConfig(
            name=("branding", "logo_backdrop"),
            django_target=("GROUPRISE", "BRANDING_LOGO_BACKDROP"),
        ),
        StringConfig(
            name=("branding", "logo_favicon"),
            django_target=("GROUPRISE", "BRANDING_LOGO_FAVICON"),
        ),
        StringConfig(
            name=("branding", "logo_square"),
            django_target=("GROUPRISE", "BRANDING_LOGO_SQUARE"),
        ),
        StringConfig(
            name=("branding", "logo_text"),
            django_target=("GROUPRISE", "BRANDING_LOGO_TEXT"),
        ),
        StringConfig(
            name=("branding", "theme_color"),
            django_target=("GROUPRISE", "BRANDING_THEME_COLOR"),
            regex="#[0-9a-fA-F]{6}$",
        ),
        AdministratorEmailsConfig(name="log_recipient_emails"),
        ListConfig(name="claims", django_target=("GROUPRISE", "CLAIMS")),
        ListConfig(
            name="entity_slug_blacklist",
            django_target=("GROUPRISE", "ENTITY_SLUG_BLACKLIST"),
            append_pre_default=(
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
            ),
            append=True,
        ),
        ListConfig(
            name="hook_script_paths",
            django_target=("GROUPRISE", "HOOK_SCRIPT_PATHS"),
        ),
        WritableDirectoryConfig(
            name="backup_path", django_target=("GROUPRISE", "BACKUP_PATH")
        ),
        IntegerConfig(
            name="score_content_age",
            django_target=("GROUPRISE", "SCORE_CONTENT_AGE"),
            minimum=0,
        ),
        IntegerConfig(
            name="upload_max_file_size",
            django_target=("GROUPRISE", "UPLOAD_MAX_FILE_SIZE"),
            minimum=0,
        ),
        IntegerConfig(
            name="feed_importer_gestalt_id",
            django_target=("GROUPRISE", "FEED_IMPORTER_GESTALT_ID"),
            minimum=1,
        ),
        IntegerConfig(
            name="operator_group_id",
            django_target=("GROUPRISE", "OPERATOR_GROUP_ID"),
            minimum=1,
        ),
        IntegerConfig(
            name="unknown_gestalt_id",
            django_target=("GROUPRISE", "UNKNOWN_GESTALT_ID"),
            minimum=1,
        ),
        # matrix settings
        MatrixAppEnableConfig(
            name=("matrix_chat", "enabled"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "ENABLED"),
        ),
        StringConfig(
            name=("matrix_chat", "domain"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "DOMAIN"),
            regex=r"[\w\-.]+$",
        ),
        StringConfig(
            name=("matrix_chat", "admin_api_url"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "ADMIN_API_URL"),
            regex=r"https?://[\w\-.]+(:\d+)?/?.*$",
        ),
        StringConfig(
            name=("matrix_chat", "bot_username"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "BOT_USERNAME"),
            regex=r"[\w\-]+$",
        ),
        StringConfig(
            name=("matrix_chat", "bot_access_token"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "BOT_ACCESS_TOKEN"),
            regex=r"[\w\-]+$",
        ),
        OIDCProviderEnableConfig(
            name=("oidc_provider", "enabled"),
            config_base_directory=base_directory,
            django_target=("OAUTH2_PROVIDER", "OIDC_ENABLED"),
        ),
    ]
    for parser in parsers:
        try:
            value = _get_nested_dict_value(config, parser.name, default=parser.default)
        except KeyError as exc:
            raise ConfigError(
                f"Failed to traverse configuration path {parser.name} trough a nested dictionary. "
                f"Please verify the dict datatype for all steps along the path."
            ) from exc
        if value is not None:
            parser.validate(value)
            parser.apply_to_settings(settings, value)
    # allow direct overrides of django configuration settings via python scripts
    django_settings_parser = ReadableFileConfig(name="extra_django_settings_filenames")
    for filename in config.get(django_settings_parser.name, []):
        django_settings_parser.validate(filename)
        import_settings_from_python(settings, filename)


def import_settings_from_python(settings, filename):
    """import a python module based on its filename and add its attributes to a dictionary

    In order to allow the customization of existing settings (e.g. "INSTALLED_APPS"), a callable
    named "post_load_hook" is executed (if it exists) right after loading the module.
    The "post_load_hook" function expects the current state of the settings namespace as a
    dictionary.  The function is supposed to manipulate it in-place.
    """
    spec = importlib.util.spec_from_file_location("django_settings", filename)
    django_settings = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(django_settings)
    except ImportError as exc:
        raise ConfigError(f"Failed to load python module '{filename}': {exc}")
    # import new settings (overriding existing ones carelessly)
    for key in dir(django_settings):
        item = getattr(django_settings, key)
        if (
            not key.startswith("_")
            and not callable(item)
            and not isinstance(item, types.ModuleType)
        ):
            settings[key] = item
    # allow customizations of existing settings (e.g. appending to "INSTALLED_APPS")
    post_load_hook = getattr(django_settings, "post_load_hook", None)
    if post_load_hook and callable(post_load_hook):
        post_load_hook(settings)


def format_django_settings(settings):
    lines = []
    for key, value in settings.items():
        if (
            not key.startswith("_")
            and not callable(value)
            and not isinstance(value, types.ModuleType)
        ):
            lines.append(f"{key} = {value}")
    return os.linesep.join(sorted(lines))
