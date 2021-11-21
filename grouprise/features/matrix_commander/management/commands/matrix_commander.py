import asyncio
import logging

import kien.command.help
import kien.command.quit
from kien.runner import ConsoleRunner

from django.core.management.base import BaseCommand

from grouprise.features.matrix_commander.commands import commander
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
        parser.add_argument(
            "--console",
            action="store_true",
            help="Run an interactive session on the console (useful for debugging).",
        )

    def handle(self, *args, log_level=None, **options):
        logging.basicConfig(level=self.LOG_LEVEL_MAP[log_level])
        if options["console"]:
            self.serve_console()
        else:
            bot = CommanderBot()
            asyncio.run(bot.serve_forever())

    def serve_console(self):
        console = CommanderConsole()
        console.commander = commander
        console.commander.compose(
            kien.command.help.command,
            kien.command.quit.command,
        )
        console.run()


class CommanderConsole(ConsoleRunner):
    def parse_args(self, args=None):
        if args is None:
            args = []
        return self.get_arg_parser().parse_args(args)
