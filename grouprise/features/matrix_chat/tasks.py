import logging

from asgiref.sync import async_to_sync, sync_to_async
from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from grouprise.core.settings import ensure_resolved_settings
from grouprise.core.tasks import TaskExpiry, TaskPriority
from grouprise.features.groups.models import Group

from .matrix_bot import ChatBot
from .settings import MATRIX_SETTINGS

logger = logging.getLogger(__name__)


@db_periodic_task(
    crontab(minute="27"),
    name="update_matrix_chat_statistics",
    priority=TaskPriority.STATISTICS,
    expires=TaskExpiry.HOURLY,
)
@ensure_resolved_settings(MATRIX_SETTINGS)
@async_to_sync
async def update_matrix_chat_statistics():
    logger.info("Update statistics for matrix chats")
    async with ChatBot() as bot:
        await bot.update_statistics()


def _get_all_groups():
    return list(Group.objects.all())


@db_periodic_task(
    crontab(minute="39"),
    name="synchronize_matrix_rooms",
    priority=TaskPriority.SYNCHRONIZATION,
    expires=TaskExpiry.HOURLY,
)
@ensure_resolved_settings(MATRIX_SETTINGS)
@async_to_sync
async def synchronize_matrix_rooms():
    """synchronize any outstanding missing room updates

    All rooms should be created on demand and all invitations should be send automatically.
    But somehow events may get lost. Thus, we trigger a periodic manual update.
    """
    logger.info("Synchronize matrix chat rooms")

    async with ChatBot() as bot:
        for group in await sync_to_async(_get_all_groups)():
            [_ async for _ in bot.synchronize_rooms_of_group(group)]
            [_ async for _ in bot.send_invitations_to_group_members(group)]
