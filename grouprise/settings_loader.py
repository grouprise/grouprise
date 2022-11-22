import base64
import copy
from distutils.version import LooseVersion
import enum
import hashlib
import importlib.util
import ipaddress
import logging
import os
import pathlib
import re
import types
from typing import Any, List, Optional, Set, Tuple, Union
import urllib.parse

"""
Determine whether the external `diskcache` implementation is available or whether Django's builtin
FileBasedCache implementation needs to be used.
Django's file-based cache suffers if a large number of cache files is stored in the flat directory.
See https://code.djangoproject.com/ticket/11260 and https://code.djangoproject.com/ticket/29994
"""
try:
    import diskcache  # noqa: F401
except ImportError:
    _file_based_cache_class = "django.core.cache.backends.filebased.FileBasedCache"
else:
    _file_based_cache_class = "diskcache.DjangoCache"
import ruamel.yaml


logger = logging.getLogger(__name__)


CONFIGURATION_FILENAME_PATTERN = re.compile(r"^[\w-]+\.yaml$")
# django-oauth-toolkit introduced OIDC support in v1.5
# https://django-oauth-toolkit.readthedocs.io/en/1.5.0/changelog.html#id1
MINIMUM_OAUTH2_VERSION = "1.5.0"
# from user configuration name to the name used by django
DATABASE_ENGINES_MAP = {
    "mysql": "django.db.backends.mysql",
    "postgis": "django.contrib.gis.db.backends.postgis",
    "postgresql": "django.db.backends.postgresql",
    "spatialite": "django.contrib.gis.db.backends.spatialite",
    "sqlite": "django.db.backends.sqlite3",
}
EMAIL_BACKENDS_MAP = {
    "console": "django.core.mail.backends.console.EmailBackend",
    "dummy": "django.core.mail.backends.dummy.EmailBackend",
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
}
CACHE_BACKENDS_MAP = {
    "dummy": "django.core.cache.backends.dummy.DummyCache",
    "filesystem": _file_based_cache_class,
    "local_memory": "django.core.cache.backends.locmem.LocMemCache",
    "memcache": "django.core.cache.backends.memcached.MemcachedCache",
    "pylibmc": "django.core.cache.backends.memcached.PyLibMCCache",
}
# The fallback cache size is used, if the cache size is not configured and the size of the target
# filesystem cannot be determined for some reason.
FALLBACK_FILESYSTEM_CACHE_SIZE_MB = 16
# The maximum size is applied only if the cache size is not configured.
MAXIMUM_FILESYSTEM_CACHE_SIZE_MB = 256


class EmailSubmissionEncryption(enum.Enum):
    PLAIN = "plain"
    STARTTLS = "starttls"
    SSL = "ssl"


class TransportSecurity(enum.Enum):
    # a django app is used for providing SSL encryption (e.g. "sslserver")
    INTEGRATED = "integrated"
    # a reverse proxy is providing transport layer security
    REVERSE_PROXY = "reverse-proxy"
    # the site is published via http-only
    DISABLED = "disabled"


class MatrixBackend(enum.Enum):
    NIO = "nio"
    CONSOLE = "console"


class FileDownloadBackend(enum.Enum):
    APACHE = "apache"
    NGINX = "nginx"
    LIGHTTPD = "lighttpd"
    NONE = "none"


def get_configuration_path_candidates():
    """return a list locations where grouprise configuration files may be looked for

    The resulting paths may not exist.
    """

    if forced_config := os.getenv("GROUPRISE_CONFIG"):
        # If a user explicitly specified a configuration location
        # we should treat it as given and should not propose any
        # alternative locations.
        return [forced_config]
    else:
        return [
            # development setup: grouprise.yaml and grouprise.conf.d/ in the current directory
            os.path.join(os.getcwd(), "grouprise.yaml"),
            os.path.join(os.getcwd(), "grouprise.conf.d"),
            os.path.expanduser("~/.config/grouprise/conf.d"),
            "/etc/grouprise/conf.d",
        ]


def get_configuration_filenames(location_candidates=None, max_level=10):
    """determine suitable configuration files based on a list of location candidates

    If no "location_candidates" are given, the result of "get_configuration_path_candidates()" is
    used.
    The locations are tested in the given order. The first candidate pointing at a file or
    pointing at a directory containing suitable files (alphanumeric characters or hyphen, with
    ".yaml" extension) is used. Directories are scanned recursively.
    All following candidates are discarded.

    A number of filenames (absolute paths) is returned.
    An empty list is returned, if no suitable files were found.
    """
    if location_candidates is None:
        location_candidates = get_configuration_path_candidates()
    if max_level == 0:
        return []
    results = []
    for path in location_candidates:
        if os.path.exists(path):
            if os.path.isdir(path):
                for filename in sorted(os.listdir(path)):
                    results.extend(
                        get_configuration_filenames(
                            [os.path.join(path, filename)],
                            max_level - 1,
                        ),
                    )
            elif os.path.isfile(path) and CONFIGURATION_FILENAME_PATTERN.match(
                os.path.basename(path)
            ):
                results.append(os.path.abspath(path))
        # stop testing further candidate locations
        # as soon as we’ve encountered a path with valid configurations
        if results:
            break
    return results


def load_settings_from_yaml_files(locations=None, error_if_missing=False):
    config_filenames = get_configuration_filenames(location_candidates=locations)
    if error_if_missing and not config_filenames:
        candidates = (
            get_configuration_path_candidates() if locations is None else locations
        )
        raise ConfigError(
            f"No suitable configuration files was found."
            f" Please ensure, that a configuration file exists in one of the following locations:"
            f" {' '.join(candidates)}"
        )
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


def guess_suitable_cache_size(path: Union[str, pathlib.Path, None]) -> int:
    """determine a reasonable size for a filesystem-backed cache based on the storage location"""
    megabyte_factor = 2 ** 20
    if not path:
        return FALLBACK_FILESYSTEM_CACHE_SIZE_MB * megabyte_factor
    try:
        vfs = os.statvfs(path)
    except OSError:
        logger.warning("Failed to determine size of cache location (%s)", path)
        return FALLBACK_FILESYSTEM_CACHE_SIZE_MB * megabyte_factor
    else:
        full_size = vfs.f_frsize * vfs.f_blocks
        # use half of the filesystem, but do not exceed the maximum
        return min(full_size / 2, MAXIMUM_FILESYSTEM_CACHE_SIZE_MB * megabyte_factor)


class ConfigError(ValueError):
    """any kind of configuration error"""


class ConfigBase:
    # We normally don’t want defaults to be stored in the settings loader, but
    # for some setting types this is practical because they control more than one
    # config variable at once.
    TOLERATE_GROUPRISE_DEFAULTS = False
    # A child class may override this attribute in order to indicate, that it expects a dictionary
    # and that the dictionary is not supposed other keys besides the listed ones.
    # A warning is emitted in case of violations.
    EXPECTED_SUB_KEYS = None

    def __init__(self, name=None, django_target=None, default=None):
        if not self.TOLERATE_GROUPRISE_DEFAULTS:
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

    def validate(self, value: Any) -> Any:
        """validate an input value and return a coerced (valid) value

        A ConfigError is raised in case of errors.
        Warnings are indicated by log messages.
        """
        if self.EXPECTED_SUB_KEYS is not None:
            if not isinstance(value, dict):
                raise ConfigError(
                    f"Configuration directive '{self.name}' must be a dict:"
                    f"{value} (type: {type(value)})"
                )
            unused_keys = set(value).difference(self.EXPECTED_SUB_KEYS)
            if unused_keys:
                logger.warning(
                    "Some attributes were unused below configuration directive '%s': %s",
                    self.name,
                    unused_keys,
                )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
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
                f"Internal error: 'django_target' for '{self.name}' must be a string,"
                f" a list of strings or a callable: {type(self.django_target)}"
                f" ('{self.django_target}')"
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
        value = super().validate(value)
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
        return value


class URLConfig(StringConfig):
    def __init__(
        self,
        *args,
        regex=None,
        min_length=None,
        sensible: bool = True,
        allowed_schemes: Optional[Set[str]] = None,
        **kwargs,
    ):
        super().__init__(*args, regex=regex, min_length=min_length, **kwargs)
        self.sensible = sensible
        self.allowed_schemes = allowed_schemes

    def validate(self, value):
        value = super().validate(value)
        url = urllib.parse.urlparse(value)
        if self.sensible:
            if not url.scheme or not url.netloc:
                raise ConfigError(
                    f"URL configured for setting '{self.name}' doesn’t look right. "
                    f"Scheme and host are missing."
                )
        if self.allowed_schemes:
            if url.scheme not in self.allowed_schemes:
                raise ConfigError(
                    f"URL configured for setting '{self.name}' uses an unsupported scheme. "
                    f"One of {', '.join(self.allowed_schemes)} is required."
                )
        return value


class BooleanConfig(ConfigBase):
    def validate(self, value):
        value = super().validate(value)
        if not isinstance(value, bool):
            raise ConfigError(
                f"Setting '{self.name}' must be a boolean value: {value} (type: {type(value)})"
            )
        return value


class IntegerConfig(ConfigBase):
    def __init__(self, *args, minimum=None, maximum=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, value):
        value = super().validate(value)
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
        return value


class DictConfig(ConfigBase):
    def validate(self, value):
        value = super().validate(value)
        if not isinstance(value, dict):
            raise ConfigError(
                f"Setting '{self.name}' must be a dict value: {value} (type: {type(value)})"
            )
        return copy.deepcopy(value)


class ChoicesConfig(ConfigBase):
    def __init__(self, *args, choices=None, **kwargs):
        self.choices = choices
        # normalize the "default" value from enum to plain text
        if isinstance(self.choices, enum.EnumMeta):
            if isinstance(kwargs.get("default"), enum.Enum):
                kwargs["default"] = kwargs["default"].value
        super().__init__(*args, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        if isinstance(self.choices, enum.EnumMeta):
            real_choices = {item.value for item in self.choices}
        else:
            real_choices = set(self.choices)
        if value not in real_choices:
            raise ConfigError(
                f"Setting '{self.name}' must be one of {real_choices}: {value}"
            )
        if isinstance(self.choices, enum.EnumMeta):
            return self.choices(value)
        else:
            return value


class ListConfig(ConfigBase):
    def __init__(self, *args, append=None, append_pre_default=None, **kwargs):
        self.append = append
        # for "append" operations: fill the list with the given values, before appending new ones
        self.append_pre_default = (
            [] if append_pre_default is None else append_pre_default
        )
        super().__init__(*args, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        if not isinstance(value, list):
            raise ConfigError(
                f"Setting '{self.name}' must be a list: {value} (type: {type(value)})"
            )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        if self.append:
            # normalize the target to a list
            if isinstance(self.django_target, (list, tuple)):
                path = self.django_target
            else:
                path = [self.django_target]
            # Do not apply the concatenation ("+=") directly to the value, but reference it via its
            # parent. Otherwise, concatenation would have no effect on tuples.
            parent = _get_nested_dict_value(settings, path[:-1], default={})
            parent.setdefault(path[-1], copy.deepcopy(self.append_pre_default))
            parent[path[-1]] += type(parent[path[-1]])(value)
        else:
            super().apply_to_settings(settings, value)


class DatabaseConfig(ConfigBase):

    EXPECTED_SUB_KEYS = {"engine", "host", "name", "password", "port", "user"}

    def validate(self, value):
        value = super().validate(value)
        engine = value.get("engine", self.default["engine"])
        if engine not in DATABASE_ENGINES_MAP:
            raise ConfigError(
                f"Invalid database engine: '{value['engine']}' "
                f"(supported: {DATABASE_ENGINES_MAP.keys()})"
            )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
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
        engine = value.get("engine", self.default["engine"])
        dest["ENGINE"] = DATABASE_ENGINES_MAP[engine]
        settings["DATABASES"] = {"default": dest}


class CacheStorageConfig(ConfigBase):

    EXPECTED_SUB_KEYS = {"backend", "location"}

    def validate(self, value):
        value = super().validate(value)
        backend = value.get("backend", self.default["backend"])
        if backend not in CACHE_BACKENDS_MAP:
            raise ConfigError(
                f"Invalid cache backend: '{backend}' "
                f"(supported: {CACHE_BACKENDS_MAP.keys()})"
            )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        dest = {}
        try:
            dest["LOCATION"] = value["location"]
        except KeyError:
            pass
        dest["OPTIONS"] = {}
        # The cache seems to be used quite heavily with around 8k cache entries (maybe due to
        # cachalot). The required storage for these 8k entries is approximately 32 MB.
        # We leave some headroom in order to track the cache usage.
        dest["OPTIONS"]["MAX_ENTRIES"] = int(value.get("max_entries", 20000))
        backend = value.get("backend", self.default["backend"])
        if (backend == "filesystem") and (os.geteuid() == 0):
            # The filesystem backend may not be enabled for a privileged user. Otherwise, files
            # and directories in the cache could end up with the wrong permissions and ownership.
            # Thus, we disable the caching completely in order to prevent coordination problems
            # between multiple processes.
            dest = {"BACKEND": CACHE_BACKENDS_MAP["dummy"]}
            logger.info("Disabling filesystem-based cache for privileged user")
        else:
            # unprivileged user: accept the chosen backend
            dest["BACKEND"] = CACHE_BACKENDS_MAP[backend]
            if backend == "filesystem":
                # determine a maximum cache size (or use the configured size)
                try:
                    max_size = value["size_limit"]
                except KeyError:
                    # determine the size of the target filesystem und use half of it
                    max_size = guess_suitable_cache_size(dest.get("LOCATION"))
                logging.info("Limiting the cache size to %d bytes", max_size)
                # This value is only used by 'diskcache.DjangoCache'.
                dest["OPTIONS"]["size_limit"] = max_size
        settings["CACHES"] = {"default": dest}


class DebugToolbarClients(ListConfig):
    """enable the [django-debug-toolbar](https://github.com/jazzband/django-debug-toolbar)

    The configuration setting may contain a list of acceptable client IP addresses.
    """

    def validate(self, value):
        value = super().validate(value)
        valid_networks = []
        for item in value:
            try:
                valid_networks.append(ipaddress.ip_network(item))
            except ValueError as exc:
                raise ConfigError(
                    f"Setting '{self.name}' must contain only valid IP addresses"
                    f" or networks, but '{item}' is malformed: {exc}"
                )
        return valid_networks

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        if value:
            import debug_toolbar

            def should_show_debug_toolbar(request):
                import ipware

                client_ip = ipware.get_client_ip(request)[0]
                if client_ip is not None:
                    client = ipaddress.ip_address(client_ip)
                    for network in value:
                        if client in network:
                            return True
                return False

            toolbar_config = settings.setdefault("DEBUG_TOOLBAR_CONFIG", {})
            toolbar_config["SHOW_TOOLBAR_CALLBACK"] = should_show_debug_toolbar
            apps = _get_nested_dict_value(settings, ["INSTALLED_APPS"], [])
            apps.append("debug_toolbar")
            middleware = _get_nested_dict_value(settings, ["MIDDLEWARE"], [])
            middleware.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
            settings.setdefault("GROUPRISE_URLS", {})["__debug__/"] = debug_toolbar.urls


class EmailBackendConfig(ChoicesConfig):
    def apply_to_settings(self, settings: dict, value: Any) -> None:
        settings["EMAIL_BACKEND"] = EMAIL_BACKENDS_MAP[value]


class EmailSubmissionEncryptionConfig(ChoicesConfig):
    def apply_to_settings(self, settings: dict, value: Any) -> None:
        value = EmailSubmissionEncryption(value)
        use_tls = False
        use_ssl = False
        if value == EmailSubmissionEncryption.PLAIN:
            port = 25
        elif value == EmailSubmissionEncryption.SSL:
            use_ssl = True
            port = 465
        elif value == EmailSubmissionEncryption.STARTTLS:
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
        value = super().validate(value)
        if not os.path.exists(value):
            raise ConfigError(
                f"The configured directory ({self.name}={value}) does not exist"
            )
        if not os.path.isdir(value):
            raise ConfigError(
                f"The configured path ({self.name}={value}) is not a directory"
            )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        """store an absolute path in the configuration"""
        abspath = os.path.abspath(value)
        super().apply_to_settings(settings, abspath)


class WritableDirectoryConfig(DirectoryConfig):
    def validate(self, value):
        value = super().validate(value)
        if not os.access(value, os.W_OK):
            raise ConfigError(
                f"The configured directory ({self.name}={value}) is not writable"
            )
        return value


class ReadableFileConfig(StringConfig):
    def validate(self, value):
        value = super().validate(value)
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
        return value


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

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        settings["LANGUAGE_CODE"] = value
        primary_tag = value.lower().replace("_", "-").split("-")[0]
        xapian_language = self.XAPIAN_LANGUAGE_MAP.get(primary_tag, self.default)
        if xapian_language:
            settings["HAYSTACK_XAPIAN_LANGUAGE"] = xapian_language


class TransportSecurityConfig(ChoicesConfig):
    def apply_to_settings(self, settings: dict, value: Any) -> None:
        if value in {TransportSecurity.INTEGRATED, TransportSecurity.REVERSE_PROXY}:
            settings["SECURE_HSTS_SECONDS"] = 365 * 24 * 3600
            settings["SESSION_COOKIE_SECURE"] = True
            settings["CSRF_COOKIE_SECURE"] = True
            settings["SECURE_SSL_REDIRECT"] = True
            settings["ACCOUNT_DEFAULT_HTTP_PROTOCOL"] = "https"
        if value == TransportSecurity.REVERSE_PROXY:
            # it is reasonable to assume that this typical header is configured on the proxy
            settings["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")
        if value == TransportSecurity.DISABLED:
            settings["ACCOUNT_DEFAULT_HTTP_PROTOCOL"] = "http"


class TemplateDirectoriesConfig(ListConfig):
    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if not os.path.exists(item):
                raise ConfigError(
                    f"Failed to find configured templates directory: {item}"
                )
            if not os.path.isdir(item):
                raise ConfigError(
                    f"Configured template location is not a directory: {item}"
                )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        # create a dummy "TEMPLATES" attribute, if it is missing (useful only for tests)
        templates = _get_nested_dict_value(settings, ["TEMPLATES"], [])
        if not templates:
            templates.append({"DIRS": []})
        templates[0]["DIRS"].extend(os.path.abspath(path) for path in value)


class StylesheetsConfig(ListConfig):
    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if not isinstance(item, dict):
                raise ConfigError(
                    f"Each item of '{self.name}' must be a dict: {item} (type: {type(item)})"
                )
            try:
                path = item["path"]
            except KeyError:
                raise ConfigError(
                    f"Missing required 'path' attribute in item of '{self.name}': {item}"
                )
            if not isinstance(path, str):
                raise ConfigError(
                    f"The 'path' value in '{self.name}' must be a string: {path}"
                    f" (type: {type(path)})"
                )
            # allow only absolute links, but forbid protocol-relative (remote) links
            if not re.match(r"^/[^/]", path):
                raise ConfigError(
                    f"The 'path' value in '{self.name}' must be an absolute (local) path"
                    f" (starting with a single slash): {path}"
                )
            if "media" in item:
                media = item["media"]
                if not isinstance(media, str):
                    raise ConfigError(
                        f"The 'media' value in '{self.name}' must be a string: {media}"
                        f" (type: {type(media)})"
                    )
            unknown_keys = set(item).difference({"path", "media"})
            if unknown_keys:
                logger.warning(
                    "Unexpected attributes %s found in item of '%s': %s",
                    unknown_keys,
                    self.name,
                    item,
                )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        raw_lines = []
        for item in value:
            path = item["path"]
            media = item.get("media")
            if media:
                line = f'<link rel="stylesheet" href="{path}" media="{media}">'
            else:
                line = f'<link rel="stylesheet" href="{path}">'
            raw_lines.append(line)
        super().apply_to_settings(settings, raw_lines)


class ScriptsConfig(ListConfig):

    SCRIPT_PATTERNS_MAP = {
        "async": '<script src="{path}" async defer />',
        "defer": '<script src="{path}" defer />',
        "blocking": '<script src="{path}" />',
    }

    @staticmethod
    def _calculate_csp_hash(script):
        hash_algorithm = "sha384"
        script_hash = hashlib.sha384(script.encode()).digest()
        base64_hash = base64.b64encode(script_hash).decode()
        return f"'{hash_algorithm}-{base64_hash}'"

    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if not isinstance(item, dict):
                raise ConfigError(
                    f"Each item of '{self.name}' must be a dict: {item} (type: {type(item)})"
                )
            if "path" in item:
                path = item["path"]
                if "content" in item:
                    raise ConfigError(
                        f"The 'path' value in '{self.name}' may not be used together with the"
                        f" 'content' value: {item}"
                    )
                if not isinstance(path, str):
                    raise ConfigError(
                        f"The 'path' value in '{self.name}' must be a string: {path}"
                        f" (type: {type(path)})"
                    )
                # allow only absolute links, but forbid protocol-relative (remote) links
                if not re.match(r"^/[^/]", path):
                    raise ConfigError(
                        f"The 'path' value in '{self.name}' must be an absolute (local) path"
                        f" (starting with a single slash): {path}"
                    )
                load_type = item.get("load", "async")
                if load_type not in self.SCRIPT_PATTERNS_MAP:
                    raise ConfigError(
                        f"The 'load' value in '{self.name}' must be one of"
                        f" async / defer / blocking: {load_type}"
                    )
            elif "content" in item:
                if "load" in item:
                    raise ConfigError(
                        f"The 'load' value in '{self.name}' may only be used together with the"
                        f" 'path' value (not 'content'): {item}"
                    )
            else:
                raise ConfigError(
                    f"Neither 'path' nor 'content' was found in '{self.name}' item: {item}"
                )

            unknown_keys = set(item).difference({"path", "load", "content"})
            if unknown_keys:
                logger.warning(
                    "Unexpected attributes %s found in item of '%s': %s",
                    unknown_keys,
                    self.name,
                    item,
                )
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        raw_lines = []
        csp_hashes = []
        for item in value:
            if "path" in item:
                path = item["path"]
                load_type = item.get("load", "async")
                pattern = self.SCRIPT_PATTERNS_MAP[load_type]
                raw_lines.append(pattern.format(path=path))
            else:
                content = item["content"].strip()
                csp_hashes.append(self._calculate_csp_hash(content))
                raw_lines.append(
                    f'<script type="application/javascript">{content}</script>'
                )
        if csp_hashes:
            # announce the hashes of our javascript snippets as trustworthy
            settings.setdefault("CSP_SCRIPT_SRC", [])
            settings["CSP_SCRIPT_SRC"] += type(settings["CSP_SCRIPT_SRC"])(csp_hashes)
        super().apply_to_settings(settings, raw_lines)


class AdministratorEmailsConfig(ListConfig):
    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if not re.match(r"[\w\-.@]*$", item):
                raise ConfigError(f"Malformed email address in '{self.name}': {item}")
        return value

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        settings["ADMINS"] = [("", item) for item in value]


class DjangoAppEnableConfig(BooleanConfig):
    def __init__(self, app_names: Union[List[str], Tuple[str, ...]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_names = app_names

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        # store the boolean value
        super().apply_to_settings(settings, value)
        if value:
            apps = _get_nested_dict_value(settings, ["INSTALLED_APPS"], [])
            apps.extend(self.app_names)


class MarixRoomIDList(ListConfig):
    ROOM_ID_REGEX = re.compile(r"^(![\w.=\-/]+:[\w.-]+\.[a-zA-Z]{2,}|)$")

    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if not self.ROOM_ID_REGEX.match(item):
                raise ConfigError(
                    f"A matrix room ID ({self.name}) contains invalid characters: {item}"
                )
        return value


class OIDCProviderEnableConfig(BooleanConfig):
    def __init__(self, *args, config_base_directory=None, **kwargs):
        self.config_base_directory = config_base_directory
        super().__init__(*args, **kwargs)

    def apply_to_settings(self, settings: dict, value: Any) -> None:
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
            # Since django-oauth-toolkit 2.0 the client is expected to use the PKCE extension by
            # default (https://django-oauth-toolkit.readthedocs.io/en/latest/changelog.html).
            # But currently (2022) matrix-synapse does not seem to support this extension.
            provider["PKCE_REQUIRED"] = False
            # The following scopes are required for the amount of attributes we want to return.
            # (see `get_additional_claims`)
            provider.setdefault("SCOPES", {}).update(
                {
                    "email": "Email scope",
                    "openid": "OpenID Connect scope",
                    "profile": "Profile scope",
                }
            )
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
            if installed_version < wanted_version:
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
                    "Thus, the location of the OIDC key file cannot be defined."
                )
            oidc_key_filename = os.path.join(self.config_base_directory, "oidc.key")
            if not os.path.exists(oidc_key_filename):
                raise ConfigError(
                    f"Missing OIDC key file ({oidc_key_filename})."
                    f" You can create it via 'openssl genrsa -out {oidc_key_filename} 4096'."
                )
            try:
                with open(oidc_key_filename, "r") as key_file:
                    oidc_key = key_file.read()
            except IOError as exc:
                raise ConfigError(
                    f"Failed to read OIDC key file ({oidc_key_filename}): {exc}"
                )
            settings["OAUTH2_PROVIDER"]["OIDC_RSA_PRIVATE_KEY"] = oidc_key


class TileServerConfig(URLConfig):
    TOLERATE_GROUPRISE_DEFAULTS = True
    REQUIRED_TOKENS = {"{s}", "{x}", "{y}", "{z}"}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("allowed_schemes", {"https"})
        super().__init__(*args, **kwargs)

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        if settings.get("GROUPRISE", {}).get("GEO", {}).get("ENABLED", False):
            super().apply_to_settings(settings, value)
            # The tile server configuration setting itself will usually not suffice if
            # CSP has been activated as images from the tile server will be blocked.
            # Fortunately we can infer the correct CSP rule for the tile server
            # from the tile server setting.
            url = urllib.parse.urlparse(value)
            settings.setdefault("CSP_IMG_SRC", tuple())
            settings["CSP_IMG_SRC"] += type(settings["CSP_IMG_SRC"])(
                [f"{url.scheme}://{url.netloc.replace('{s}', '*')}"]
            )

    def validate(self, value):
        value = super().validate(value)
        for required_token in self.REQUIRED_TOKENS:
            if required_token not in value:
                raise ConfigError(
                    f"The tile server URL configured for setting '{self.name}' must contain the "
                    f"tokens {', '.join(self.REQUIRED_TOKENS)}."
                )
        return value


class CoordinatesConfig(ListConfig):
    def validate(self, value):
        value = super().validate(value)
        for item in value:
            if (
                not isinstance(item, list)
                or len(item) != 2
                or not isinstance(item[0], (int, float))
                or not isinstance(item[1], (int, float))
            ):
                raise ConfigError(
                    f"Setting '{self.name}' must be a list of "
                    f"latitude/longitude coordinates as two-element float tuples."
                )
        return value


class FileDownloadConfig(ChoicesConfig):
    TOLERATE_GROUPRISE_DEFAULTS = True

    def apply_to_settings(self, settings: dict, value: Any) -> None:
        if value != FileDownloadBackend.NONE:
            if value == FileDownloadBackend.APACHE:
                from django_downloadview.nginx import x_sendfile as wrapper
            elif value == FileDownloadBackend.LIGHTTPD:
                from django_downloadview.lighttpd import x_sendfile as wrapper
            elif value == FileDownloadBackend.NGINX:
                from django_downloadview.nginx import x_accel_redirect as wrapper
            else:
                raise KeyError(f"Unknown FileDownloadBackend: {value}")
            # We do not use django-downloadview's middleware for optimizing media delivery.
            # Instead we just apply the decorator "get_accelerated_download_view" to the few views,
            # which deliver a file from the media directory.
            super().apply_to_settings(settings, wrapper)


def _get_nested_dict_value(data, path, default=None, remove=False):
    if not isinstance(data, dict):
        raise KeyError(f"Container is not a dictionary: {data}")
    elif len(path) == 0:
        if remove:
            raise ValueError(
                "Removal of settings key is not possible, if the given path is empty"
            )
        return data
    elif len(path) == 1:
        data.setdefault(path[0], default)
        if remove:
            return data.pop(path[0], default)
        else:
            return data.get(path[0], default)
    else:
        data.setdefault(path[0], {})
        return _get_nested_dict_value(
            data[path[0]], path[1:], default=default, remove=remove
        )


def recursively_normalize_dict_keys_to_lower_case(data):
    """walk through the data (through dicts and lists) and change all dict keys to lower case"""
    if isinstance(data, dict):
        return {
            key.lower(): recursively_normalize_dict_keys_to_lower_case(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [recursively_normalize_dict_keys_to_lower_case(item) for item in data]
    else:
        return data


def remove_empty_dicts(_dict: dict):
    """removes empty dicts in a nested dict structure"""
    for key in list(_dict.keys()):
        if isinstance(_dict[key], dict):
            remove_empty_dicts(_dict[key])
            if not _dict[key]:
                _dict.pop(key)


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


def import_settings_from_yaml(settings, locations=None, error_if_missing=False):
    """import grouprise settings from one or more yaml-formatted setting files

    The setting filenames are discovered based on the given list of suggested location candidates.
    The settings are merged in a trivial fashion: later configuration settings override existing
    settings with the same name.

    The special configuration directive "extra_django_settings_filenames" may contain a list of
    filenames, that will be loaded as python modules.
    See "import_settings_from_python" for details.
    """
    config = load_settings_from_yaml_files(locations, error_if_missing=error_if_missing)
    base_directory = get_config_base_directory(locations)
    return import_settings_from_dict(settings, config, base_directory=base_directory)


def import_settings_from_dict(settings: dict, config: dict, base_directory=None):
    """
    settings: the target dictionary to be populated (e.g. "locals()" in settings.py)
    config: the source dictionary parsed from a grouprise configuration file
    """
    # We want to tolerate settings with upper-case instead of lower-case keys.
    # This should simplify the migration from Django-based settings to the yaml-based settings.
    config = recursively_normalize_dict_keys_to_lower_case(config)
    default_domain = "example.org"
    configured_domain = config.get("domain", default_domain)
    parsers = [
        StringConfig(
            # TODO: clarify whether the database or the configuration should be the source of truth
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
        WritableDirectoryConfig(name="data_path", django_target="GROUPRISE_DATA_DIR"),
        CacheStorageConfig(name="cache_storage", default={"backend": "local_memory"}),
        IntegerConfig(
            name="session_cookie_age", django_target="SESSION_COOKIE_AGE", minimum=0
        ),
        TransportSecurityConfig(
            name="transport_security",
            choices=TransportSecurity,
            default=TransportSecurity.REVERSE_PROXY,
        ),
        BooleanConfig(name="debug", django_target="DEBUG"),
        DebugToolbarClients(name="debug_toolbar_clients"),
        LanguageCodeConfig(
            name="language_code", default="de-de", regex=r"^\w+([-_]\w+)?$"
        ),
        StringConfig(
            name="time_zone", default="Europe/Berlin", django_target="TIME_ZONE"
        ),
        ListConfig(
            name="extra_allowed_hosts", django_target="ALLOWED_HOSTS", append=True
        ),
        EmailBackendConfig(
            name=("email_submission", "backend"), choices=EMAIL_BACKENDS_MAP.keys()
        ),
        # encryption needs to be applied *before* "EMAIL_PORT", since it selects a default port
        EmailSubmissionEncryptionConfig(
            name=("email_submission", "encryption"),
            choices=EmailSubmissionEncryption,
            default=EmailSubmissionEncryption.PLAIN,
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
        BooleanConfig(
            name=("events", "enable_repetitions"),
            django_target=("GROUPRISE", "EVENTS", "ENABLE_REPETITIONS"),
        ),
        BooleanConfig(
            name=("events", "enable_attendance"),
            django_target=("GROUPRISE", "EVENTS", "ENABLE_ATTENDANCE"),
        ),
        BooleanConfig(
            name=("events", "allow_attendance_management_for_group_members"),
            django_target=(
                "GROUPRISE",
                "EVENTS",
                "ALLOW_ATTENDANCE_MANAGEMENT_FOR_GROUP_MEMBERS",
            ),
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
        StylesheetsConfig(
            name="stylesheets", django_target=("GROUPRISE", "HEADER_ITEMS"), append=True
        ),
        ScriptsConfig(
            name="scripts", django_target=("GROUPRISE", "HEADER_ITEMS"), append=True
        ),
        FileDownloadConfig(
            name="file_download_backend",
            choices=FileDownloadBackend,
            django_target=("GROUPRISE", "FILE_DOWNLOAD_WRAPPER"),
            default=FileDownloadBackend.NONE,
        ),
        # geo settings
        DjangoAppEnableConfig(
            name=("geo", "enabled"),
            django_target=("GROUPRISE", "GEO", "ENABLED"),
            app_names=(
                "grouprise.features.geo",
                "django.contrib.gis",
            ),
        ),
        TileServerConfig(
            name=("geo", "tile_server", "url"),
            django_target=("GROUPRISE", "GEO", "TILE_SERVER", "URL"),
            default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        ),
        StringConfig(
            name=("geo", "tile_server", "attribution"),
            django_target=("GROUPRISE", "GEO", "TILE_SERVER", "ATTRIBUTION"),
        ),
        ListConfig(
            name=("geo", "location_selector", "center"),
            django_target=("GROUPRISE", "GEO", "LOCATION_SELECTOR", "CENTER"),
        ),
        IntegerConfig(
            name=("geo", "location_selector", "zoom"),
            django_target=("GROUPRISE", "GEO", "LOCATION_SELECTOR", "ZOOM"),
        ),
        # matrix settings
        DjangoAppEnableConfig(
            name=("matrix_chat", "enabled"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "ENABLED"),
            app_names=("grouprise.features.matrix_chat",),
        ),
        ChoicesConfig(
            name=("matrix_chat", "backend"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "BACKEND"),
            choices=MatrixBackend,
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
        MarixRoomIDList(
            name=("matrix_chat", "public_listener_rooms"),
            django_target=("GROUPRISE", "MATRIX_CHAT", "PUBLIC_LISTENER_ROOMS"),
        ),
        DjangoAppEnableConfig(
            name=("matrix_commander", "enabled"),
            django_target=("GROUPRISE", "MATRIX_COMMANDER", "ENABLED"),
            app_names=("grouprise.features.matrix_commander",),
        ),
        ChoicesConfig(
            name=("matrix_commander", "backend"),
            django_target=("GROUPRISE", "MATRIX_COMMANDER", "BACKEND"),
            choices=MatrixBackend,
        ),
        StringConfig(
            name=("matrix_commander", "bot_id"),
            django_target=("GROUPRISE", "MATRIX_COMMANDER", "BOT_ID"),
        ),
        StringConfig(
            name=("matrix_commander", "bot_access_token"),
            django_target=("GROUPRISE", "MATRIX_COMMANDER", "BOT_ACCESS_TOKEN"),
            regex=r"[\w\-]+$",
        ),
        MarixRoomIDList(
            name=("matrix_commander", "admin_rooms"),
            django_target=("GROUPRISE", "MATRIX_COMMANDER", "ADMIN_ROOMS"),
        ),
        StringConfig(
            name=("sentry", "dsn"),
            django_target="SENTRY_DSN",
        ),
        DictConfig(
            name=("sentry", "init_options"),
            django_target="SENTRY_INIT_OPTIONS",
        ),
        OIDCProviderEnableConfig(
            name=("oidc_provider", "enabled"),
            config_base_directory=base_directory,
            django_target=("OAUTH2_PROVIDER", "OIDC_ENABLED"),
        ),
    ]
    for parser in parsers:
        value_path = [parser.name] if isinstance(parser.name, str) else parser.name
        try:
            value = _get_nested_dict_value(
                config, value_path, default=parser.default, remove=True
            )
        except KeyError as exc:
            raise ConfigError(
                f"Failed to traverse configuration path {parser.name} through a nested dictionary."
                f" Please verify the dict datatype for all steps along the path."
            ) from exc
        if value is not None:
            value = parser.validate(value)
            parser.apply_to_settings(settings, value)
    # allow direct overrides of django configuration settings via python scripts
    django_settings_parser = ReadableFileConfig(name="extra_django_settings_filenames")
    for filename in config.pop(django_settings_parser.name, []):
        django_settings_parser.validate(filename)
        import_settings_from_python(settings, filename)
    # remove all empty dictionaries, so we can report any remaining data
    # as unprocessed configuration options
    remove_empty_dicts(config)
    if config:
        logger.warning(
            "Some configuration settings were not processed (%s)."
            " Maybe they are misspelled or are outdated?",
            config,
        )


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


def convert_django_settings_to_dict(django_settings):
    settings = {}
    for key in dir(django_settings):
        value = getattr(django_settings, key)
        if not key.startswith("_") and not callable(value):
            settings[key] = value
    return settings


def format_django_settings(settings: dict):
    lines = []
    for key, value in settings.items():
        if (
            not key.startswith("_")
            and not callable(value)
            and not isinstance(value, types.ModuleType)
        ):
            lines.append(f"{key} = {value}")
    return os.linesep.join(sorted(lines))
