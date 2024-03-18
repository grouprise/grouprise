import contextlib
import functools
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.templatetags.static import static

try:
    _GR = settings.GROUPRISE
except AttributeError:
    _GR = {}


class LazySettingsResolver:
    """storage class for settings

    Features:
    * optional lazy evaluation
        * For example the evaluation of "Site.objects.get_current().domain" can be delayed
          until it is really required, since database queries are not available in the
          pre-configure phase (e.g. while "urls.py" is parsed).
    * allow temporary override of specific settings
    """

    def __init__(self, **kwargs):
        def lazy_resolver(func):
            return functools.lru_cache()(func)

        self._attribute_names = set()
        self._unresolved_attributes = {}
        # set the attribute values or (for callables) a lazy evaluator
        for key, value in kwargs.items():
            if callable(value):
                self._unresolved_attributes[key] = value
            else:
                # simple attribute values
                setattr(self, key, value)
            self._attribute_names.add(key)

    def __getattr__(self, name):
        """implement a lazy evaluation mechanism (similar to functools.cached_property)

        This function is supposed to be called for each key in `self._unresolved_attributes`, when
        it is accessed for the first time.

        The `functools.cached_property` decorator could be used instead, but it is only available
        since Python 3.9.
        Note: the `cached_property` would need to be assigned to the class (not the instance) and
        `__set_name__` needs to be called explicitly on the new `cached_property` instance.
        See https://bugs.python.org/issue38517
        """
        try:
            value_func = self._unresolved_attributes[name]
        except KeyError:
            raise AttributeError(f"Missing settings key '{name}' in {type(self)}")
        else:
            # first access to the lazy-evaluation attribute: finally set the calculated value
            value = value_func()
            setattr(self, name, value)
            # Tolerate a missing key, since multiple accesses may occur in parallel, if
            # `value_func` is asynchronous.
            self._unresolved_attributes.pop(name, None)
            return value

    def resolve_lazy_settings(self):
        """force the resolution of all "lazy" configuration values

        This method should be called right after the app is ready in order to ensure, that no
        unexpected sync calls (e.g. depending on the ORM) are executed in an async context.
        """
        for name in list(self._unresolved_attributes):
            getattr(self, name)

    @contextlib.contextmanager
    def temporary_override(self, **kwargs):
        """Allow temporary manipulation of specific settings (e.g. for tests)"""
        previous_content = {}
        for key, value in kwargs.items():
            previous_content[key] = getattr(self, key)
            setattr(self, key, value)
        yield self
        for key, value in previous_content.items():
            setattr(self, key, value)


def ensure_resolved_settings(settings):
    """decorator for resolving a LazySettingsResolver instance before a function is executed

    This decorator is intended for situations, where a function is wrapped into `async_to_sync`,
    but it is not guaranteed, that ORM-related functions (which are forbidden in an async context
    in Django 3.x and 4.x) are needed at runtime.
    """

    def wrapper_outer(func):
        @functools.wraps(func)
        def wrapper_inner(*args, **kwargs):
            settings.resolve_lazy_settings()
            return func(*args, **kwargs)

        return wrapper_inner

    return wrapper_outer


def get_grouprise_baseurl():
    return "{proto}://{domain}".format(
        proto=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL,
        domain=get_grouprise_site().domain,
    )


def get_grouprise_site():
    return Site.objects.get_current()


CORE_SETTINGS = LazySettingsResolver(
    # branding
    CLAIMS=_GR.get("CLAIMS", []),
    HEADER_ITEMS=_GR.get("HEADER_ITEMS", []),
    FOOTER_ITEMS=_GR.get("FOOTER_ITEMS", []),
    LOGO_BACKDROP=_GR.get(
        "BRANDING_LOGO_BACKDROP", static("core/logos/logo-backdrop.svg")
    ),
    LOGO_FAVICON=_GR.get("BRANDING_LOGO_FAVICON", static("core/logos/logo-square.png")),
    LOGO_SQUARE=_GR.get("BRANDING_LOGO_SQUARE", static("core/logos/logo-square.svg")),
    LOGO_TEXT=_GR.get("BRANDING_LOGO_TEXT", static("core/logos/logo-text.svg")),
    THEME_COLOR=_GR.get("BRANDING_THEME_COLOR", "#2a62ac"),
    # mail handling
    COLLECTOR_MAILBOX_ADDRESS=_GR.get("COLLECTOR_MAILBOX_ADDRESS", None),
    DEFAULT_DISTINCT_FROM_EMAIL=_GR.get(
        "DEFAULT_DISTINCT_FROM_EMAIL",
        lambda: "noreply+{slug}@" + get_grouprise_site().domain,
    ),
    DEFAULT_REPLY_TO_EMAIL=_GR.get(
        "DEFAULT_REPLY_TO_EMAIL",
        lambda: "reply+{reply_key}@" + get_grouprise_site().domain,
    ),
    MAILINGLIST_ENABLED=_GR.get("MAILINGLIST_ENABLED", False),
    POSTMASTER_EMAIL=_GR.get(
        "POSTMASTER_EMAIL", lambda: "postmaster@" + get_grouprise_site().domain
    ),
    # content import
    FEED_IMPORTER_GESTALT_ID=_GR.get("FEED_IMPORTER_GESTALT_ID", None),
    OPERATOR_GROUP_ID=_GR.get("OPERATOR_GROUP_ID", 1),
    UNKNOWN_GESTALT_ID=_GR.get("UNKNOWN_GESTALT_ID", 1),
    # local administration
    BACKUP_PATH=_GR.get("BACKUP_PATH", os.getcwd()),
    HOOK_SCRIPT_PATHS=_GR.get("HOOK_SCRIPT_PATHS", []),
    # miscellaneous
    ENTITY_SLUG_BLACKLIST=_GR.get(
        "ENTITY_SLUG_BLACKLIST",
        [
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
        ],
    ),
    SCORE_CONTENT_AGE=_GR.get("SCORE_CONTENT_AGE", 100),
    UPLOAD_MAX_FILE_SIZE=_GR.get("UPLOAD_MAX_FILE_SIZE", 10),
    # the wrapper is a callable - we protect it from being evaluated by the LazySettingsResolver
    FILE_DOWNLOAD_WRAPPER=lambda: _GR.get("FILE_DOWNLOAD_WRAPPER", None),
)
