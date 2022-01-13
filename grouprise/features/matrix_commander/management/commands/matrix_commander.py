import logging

import kien.command.help
import kien.command.quit
from django.core.management.base import BaseCommand
from kien.runner import ConsoleRunner

from grouprise.core.utils import run_async
from grouprise.features.matrix_chat.matrix_bot import MatrixError
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
            try:
                run_async(self.serve_bot())
            except KeyboardInterrupt:
                pass

    async def serve_bot(self):
        try:
            async with CommanderBot() as bot:
                await bot.serve_forever()
        except MatrixError as exc:
            self.stderr.write(self.style.ERROR(f"Matrix error: {exc}"))

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
