import logging

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

import grouprise.core.scores
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="23"))
def update_scores():
    logger.info("Updating scores of gestalts and groups")
    grouprise.core.scores.update(Gestalt)
    grouprise.core.scores.update(Group)
