from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Executes production environment tasks required for successful operation"

    def handle(self, *args, **options):
        self.stderr.write("Executing migrations...")
        call_command("migrate", interactive=False)
        self.stderr.write("Collecting assets...")
        call_command("collectstatic", clear=True, interactive=False)
