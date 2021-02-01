import sys

import django

from grouprise.features.imports.feeds import run_feed_import_for_groups


class Command(django.core.management.base.BaseCommand):
    def handle(self, *args, **options):
        processed_groups = run_feed_import_for_groups()
        if processed_groups is None:
            self.stderr.write(self.style.ERROR("Failed to import feeds."))
            sys.exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Processed feeds of {len(processed_groups):d} groups."
                )
            )
