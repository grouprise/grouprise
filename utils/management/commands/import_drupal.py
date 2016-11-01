from django.core.management.base import BaseCommand
import utils.import_drupal


class Command(BaseCommand):

    help = "Importieren der historischen Drupal-Instanz"

    def handle(self, *args, **options):
        utils.import_drupal.run_import()
