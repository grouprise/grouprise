import sys

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

import cas_server.models as models


class Command(BaseCommand):
    args = ""
    help = "Enable or disable CAS authentication for the attached matrix server"

    def add_arguments(self, parser):
        default_app_url = "https://{}:8448/".format(Site.objects.get_current().domain)
        parser.add_argument("action", choices=("add", "remove"))
        parser.add_argument("label", type=str)
        parser.add_argument("--app-url", type=str, default=default_app_url)

    def get_cas_service_pattern(self, label):
        patterns = models.ServicePattern.objects.filter(name=label)
        try:
            return patterns[0]
        except IndexError:
            return None

    def handle(self, *args, **options):
        action = options["action"]
        label = options["label"]
        app_url = options["app_url"]
        if action == "add":
            existing = self.get_cas_service_pattern(label)
            if existing is None:
                new_obj = models.ServicePattern(pattern=app_url, name=label)
                new_obj.save()
                self.stdout.write(
                    self.style.SUCCESS("Added service pattern for authentication")
                )
            elif existing.pattern == app_url:
                self.stdout.write(
                    self.style.NOTICE("Keeping existing service pattern unchanged")
                )
            else:
                existing.pattern = app_url
                existing.save()
                self.stdout.write(
                    self.style.SUCCESS("Modified existing service pattern")
                )
        elif action == "remove":
            existing = self.get_cas_service_pattern(label)
            if existing is None:
                self.stdout.write(
                    self.style.NOTICE("No matching service pattern found")
                )
            else:
                existing.delete()
                self.stdout.write(
                    self.style.SUCCESS("Removed existing service pattern")
                )
        else:
            self.stderr.write(
                self.style.ERROR("Invalid action requested: {}".format(action))
            )
            sys.exit(1)
