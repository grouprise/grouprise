import datetime
import enum
import os
import tarfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from grouprise.core.settings import CORE_SETTINGS

EXCLUDE_FILENAMES = {"CACHE", ".gitkeep"}


def assemble_filename(directory, prefix, filename, suffix):
    return os.path.abspath(
        os.path.join(
            directory,
            "{prefix}{filename}{suffix}".format(
                **{
                    "prefix": "{}_".format(prefix) if prefix else "",
                    "filename": (
                        filename
                        or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    ),
                    "suffix": suffix,
                }
            ),
        )
    )


class Compression(enum.Enum):
    """compression types supported by the tarfile module"""

    NONE = (0, "none", ".tar", "")
    GZIP = (1, "gzip", ".tar.gz", "gz")
    BZIP2 = (2, "bzip2", ".tar.bz2", "bz2")
    LZMA = (3, "lzma", ".tar.xz", "xz")

    def __init__(self, weight, key, filename_extension, tarfile_type):
        self.weight = weight
        self.key = key
        self.filename_extension = filename_extension
        self.tarfile_type = tarfile_type

    @classmethod
    def get_by_key(cls, wanted_key):
        for item in cls:
            if item.key == wanted_key:
                return item
        else:
            allowed_keys = ", ".join(item.key for item in sorted(cls))
            raise KeyError(
                f"Invalid compression method ('{wanted_key}') requested."
                f" Choose one of: {allowed_keys}"
            )

    def __lt__(self, other):
        return self.weight < other.weight


class Command(BaseCommand):
    help = "export the content of the media directory"

    def add_arguments(self, parser):
        parser.add_argument("--prefix", default="media", help="prefix for the filename")
        parser.add_argument(
            "--output-dir", default=CORE_SETTINGS.BACKUP_PATH, help="backup storage dir"
        )
        parser.add_argument("--output-file", default=None, help="backup filename")
        parser.add_argument(
            "--compression",
            default=Compression.GZIP.key,
            choices=tuple(c.key for c in sorted(Compression)),
            help="Compression algorithm to be used for export archive",
        )

    def handle(self, *args, **options):
        compression = Compression.get_by_key(options.get("compression"))
        prefix = options.get("prefix")
        output_dir = options.get("output_dir")
        output_file = options.get("output_file")
        output_filename = assemble_filename(
            output_dir, prefix, output_file, suffix=compression.filename_extension
        )
        # use a temporary filename while the file is incomplete
        partial_output_filename = output_filename + ".part"
        media_dir = settings.MEDIA_ROOT

        def reset_owner_and_ignore_excludes(tarinfo: tarfile.TarInfo):
            tarinfo.uid = tarinfo.gid = 0
            tarinfo.uname = tarinfo.gname = "root"
            return tarinfo

        try:
            output = tarfile.open(
                partial_output_filename, mode=f"w:{compression.tarfile_type}"
            )
            for filename in os.listdir(media_dir):
                if filename not in EXCLUDE_FILENAMES:
                    output.add(
                        os.path.join(media_dir, filename),
                        arcname=filename,
                        filter=reset_owner_and_ignore_excludes,
                    )
        except FileNotFoundError as exc:
            raise CommandError(f"Failed to create dump output file: {exc}")
        except tarfile.TarError as exc:
            os.unlink(partial_output_filename)
            raise CommandError(f"Failed to create archive: {exc}")
        else:
            output.close()
            try:
                os.rename(partial_output_filename, output_filename)
            except OSError as exc:
                raise CommandError(
                    "Failed to move database backup file to its final location: {}".format(
                        exc
                    )
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created media backup: {partial_output_filename}"
                )
            )
