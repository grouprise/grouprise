import contextlib
import logging

from haystack import connections
from haystack.constants import DEFAULT_ALIAS
from haystack.exceptions import HaystackError
from haystack.management.commands import update_index

logger = logging.getLogger(__name__)


class HaystackIndexUpdater:
    _can_apply_haystack_log_filter = hasattr(update_index, "LOG")

    class HaystackUpdateFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if record.levelno == logging.ERROR and record.msg.startswith(
                "Error updating"
            ):
                return False
            return True

    @staticmethod
    def _has_haystack_models_to_index():
        unified_index = connections[DEFAULT_ALIAS].get_unified_index()
        for search_index in unified_index.get_indexes().values():
            if len(search_index.index_queryset()) > 0:
                return True
        return False

    @contextlib.contextmanager
    def _get_command(self):
        update_index_log_filter = self.HaystackUpdateFilter()
        if self._can_apply_haystack_log_filter:
            # management commands are usually meant for execution in a terminal environment,
            # which is why the error logging in the command itself is understandable. In our
            # case we want to handle some exceptions and don’t want to spam the log with them,
            # so we apply a log filter.
            update_index.LOG.addFilter(update_index_log_filter)
        try:
            yield update_index.Command()
        except HaystackError as exc:
            # Xapian doesn’t populate its database if there aren’t any models to index.
            # This is fine when populating the index but raises exceptions if we also
            # try to remove items from the index, because then haystack tries to query
            # outdated items from the index, but xapian can’t find an index to query.
            # This is only a problem with a fresh database and why we silently ignore
            # runtime errors if there aren’t any models yet.
            if (
                not str(exc).startswith("Unable to open index at")
                or self._has_haystack_models_to_index()
            ):
                raise
        finally:
            if self._can_apply_haystack_log_filter:
                update_index.LOG.removeFilter(update_index_log_filter)

    def update(self):
        logger.info("Starting update of search index")
        # Sadly the haystack command "update_index" contains a lot of complicated logic.
        # Thus, we need to execute it directly.
        with self._get_command() as update_command:
            update_command.handle(remove=True)
        logger.info("Finished update of search index")
