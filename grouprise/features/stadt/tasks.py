import logging

from haystack.management.commands.update_index import Command as UpdateIndexCommand
from huey import crontab
from huey.contrib.djhuey import db_periodic_task

import grouprise.core.scores
from grouprise.core.tasks import TaskExpiry, TaskPriority
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group

logger = logging.getLogger(__name__)


@db_periodic_task(
    crontab(minute="23", hour="*/3"),
    priority=TaskPriority.STATISTICS,
    expires=TaskExpiry.HOURLY,
)
def update_scores():
    logger.info("Updating scores of gestalts and groups")
    grouprise.core.scores.update(Gestalt)
    grouprise.core.scores.update(Group)


@db_periodic_task(
    crontab(minute="12"), priority=TaskPriority.STATISTICS, expires=TaskExpiry.HOURLY
)
def update_search_index():
    logger.info("Starting update of search index")
    # Sadly the haystack command "update_index" contains a lot of complicated logic.
    # Thus, we need to execute it directly.
    UpdateIndexCommand().handle(remove=True)
    logger.info("Finished update of search index")
