import logging

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from grouprise.features.imports.feeds import run_feed_import_for_groups

logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="46"))
def import_feed_for_groups():
    logger.info("Update website feeds for groups")
    run_feed_import_for_groups()
