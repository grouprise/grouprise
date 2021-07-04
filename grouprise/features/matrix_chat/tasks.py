import asyncio
import logging

from huey import crontab
from huey.contrib.djhuey import db_periodic_task

from .matrix_bot import MatrixBot


logger = logging.getLogger(__name__)


@db_periodic_task(crontab(minute="27"))
def update_matrix_chat_statiscs():
    logger.info("Update statistics for matrix chats")

    async def update():
        async with MatrixBot() as bot:
            await bot.update_statistics()

    asyncio.run(update())
