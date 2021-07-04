import asyncio
import logging

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from grouprise.features.groups.models import Group
from .matrix_bot import MatrixBot


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="27"))
def update_matrix_chat_statiscs():
    logger.info("Update statistics for matrix chats")

    async def update():
        async with MatrixBot() as bot:
            await bot.update_statistics()

    asyncio.run(update())


@db_periodic_task(crontab(minute="39"))
def synchronize_matrix_rooms():
    """synchronize any outstanding missing room updates

    All rooms should be created on demand and all invitations should be send automatically.
    But somehow events may get lost, thus we trigger a periodic manual update.
    """
    logger.info("Synchronize matrix chat rooms")

    async def synchronize():
        async with MatrixBot() as bot:
            for group in Group.objects.all():
                async for _ in bot.synchronize_rooms_of_group(group):  # noqa: F841
                    pass
                async for _ in bot.send_invitations_to_group_members(
                    group
                ):  # noqa: F841
                    pass

    asyncio.run(synchronize())
