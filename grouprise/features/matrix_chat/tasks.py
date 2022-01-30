import logging

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from grouprise.core.utils import run_async
from grouprise.features.groups.models import Group

from .matrix_bot import ChatBot

logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="27"))
def update_matrix_chat_statistics():
    logger.info("Update statistics for matrix chats")

    async def update():
        async with ChatBot() as bot:
            await bot.update_statistics()

    run_async(update())


@db_periodic_task(crontab(minute="39"))
def synchronize_matrix_rooms():
    """synchronize any outstanding missing room updates

    All rooms should be created on demand and all invitations should be send automatically.
    But somehow events may get lost, thus we trigger a periodic manual update.
    """
    logger.info("Synchronize matrix chat rooms")

    async def synchronize():
        async with ChatBot() as bot:
            for group in Group.objects.all():
                [_ async for _ in bot.synchronize_rooms_of_group(group)]
                [_ async for _ in bot.send_invitations_to_group_members(group)]

    run_async(synchronize())
