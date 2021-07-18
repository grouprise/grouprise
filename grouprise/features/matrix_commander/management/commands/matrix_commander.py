import asyncio
import logging

from django.core.management.base import BaseCommand

from grouprise.features.matrix_commander.matrix_bot import CommanderBot


class Command(BaseCommand):
    help = "Run a matrix bot capable of reacting to commands in configured matrix rooms"

    LOG_LEVEL_MAP = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--log-level",
            default="warning",
            choices=set(self.LOG_LEVEL_MAP),
            help="Specify a log level",
        )

    def handle(self, *args, log_level=None, **options):
        logging.basicConfig(level=self.LOG_LEVEL_MAP[log_level])
        bot = CommanderBot()
        asyncio.run(bot.serve_forever())
