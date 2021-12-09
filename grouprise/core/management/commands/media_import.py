import os
import shutil
import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "import a dump into the media directory"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            required=True,
            help="filename of the media archive to be imported",
        )
        parser.add_argument(
            "--media-dir",
            default=settings.MEDIA_ROOT,
            help="target directory for media import",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="delete the existing files in the media directory before extracting the archive",
        )

    def handle(self, *args, **options):
        archive_filename = options.get("filename")
        media_dir = options.get("media_dir")
        clear_before_import = options.get("clear")
        try:
            if not os.path.exists(media_dir):
                os.makedirs(media_dir, exist_ok=True)
        except OSError as exc:
            raise CommandError(f"Failed to create media directory ({media_dir}): {exc}")
        if clear_before_import:
            try:
                for node in os.listdir(media_dir):
                    full_path = os.path.join(media_dir, node)
                    try:
                        if os.path.isfile(full_path) or os.path.islink(full_path):
                            os.remove(full_path)
                        elif os.path.isdir(full_path):
                            shutil.rmtree(full_path)
                        else:
                            self.stderr.write(
                                self.style.WARNING(
                                    f"Ignoring non-trivial existing node below media directory"
                                    f" ({media_dir}) during clear operation: {full_path}"
                                )
                            )
                    except OSError as exc:
                        raise CommandError(
                            f"Failed to delete item below media directory ({full_path}): {exc}"
                        )
            except OSError as exc:
                raise CommandError(
                    f"Failed to clear media directory before import: {exc}"
                )
        try:
            archive = tarfile.open(archive_filename, mode="r:*")
            archive.extractall(path=media_dir)
        except FileNotFoundError:
            raise CommandError(f"Failed to find archive: {archive_filename}")
        except tarfile.TarError as exc:
            raise CommandError(f"Failed to extract archive ({archive_filename}): {exc}")
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported media archive: {archive_filename}"
            )
        )
