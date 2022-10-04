import cProfile
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "run a command and export its profiling statistics into a file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-file", required=True, help="profiling export filename"
        )

    def handle(self, *args, **options):
        commands = sys.stdin.read()
        output_filename = options.get("output_file")
        cProfile.run(commands, filename=output_filename)
