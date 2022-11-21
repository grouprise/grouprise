import datetime
import getpass
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from grouprise.core.settings import CORE_SETTINGS


def create_filename(directory, prefix, filename=None, suffix=""):
    return os.path.abspath(
        os.path.join(
            directory,
            "{prefix}{filename}{suffix}".format(
                **{
                    "prefix": "{}_".format(prefix) if prefix else "",
                    "filename": filename
                    or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".sql",
                    "suffix": suffix,
                }
            ),
        )
    )


def d(dict, key, default=None):
    try:
        value = dict[key]
        return value if value else default
    except KeyError:
        return default


def create_psql_uri(db):
    uri = "postgresql://"
    user = d(db, "USER", False)
    password = d(db, "PASSWORD", False)
    host = d(db, "HOST", "localhost")
    name = d(db, "NAME")
    if user and password:
        uri += "{}:{}@".format(user, password)
    elif user:
        uri += "{}@".format(user)
    elif host == "localhost" and password is False:
        if user is False or user == getpass.getuser():
            # the database is on this host, no password was set
            # and either no user was set or the command runs as the defined user
            # this probably means that we postgres' username-matching
            # authentication mechanism
            return name
    uri += "{}/{}".format(host, name)
    return uri


class Command(BaseCommand):
    help = "exports the currently configured database"

    def add_arguments(self, parser):
        parser.add_argument("--prefix", default="", help="prefix for the filename")
        parser.add_argument(
            "--output-dir", default=CORE_SETTINGS.BACKUP_PATH, help="backup storage dir"
        )
        parser.add_argument("--output-file", default=None, help="backup filename")

    def handle(self, *args, **options):
        prefix = options.get("prefix")
        output_dir = options.get("output_dir")
        output_file = options.get("output_file")
        db = settings.DATABASES["default"]
        engine = db["ENGINE"].split(".")[-1]
        output_filename = create_filename(output_dir, prefix, output_file, suffix=".gz")
        # use a temporary filename while the file is incomplete
        partial_output_filename = output_filename + ".part"

        if engine == "sqlite3":
            dump_call = ("sqlite3", db["NAME"], ".dump")
        elif engine in {"postgresql", "postgis"}:
            dump_call = (
                "pg_dump",
                "--no-owner",
                "--no-privileges",
                create_psql_uri(db),
            )
        else:
            raise CommandError("database backup not supported with %s engine" % engine)
        try:
            with open(partial_output_filename, "wb") as dump_out:
                try:
                    dump_proc = subprocess.Popen(
                        dump_call,
                        cwd="/",
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                except FileNotFoundError:
                    raise CommandError(
                        'executable "{}" seems to be missing'.format(dump_call[0])
                    )
                # compress the output
                # Sadly we cannot use the gzip module for on-the-fly compression
                # (e.g. "gzip.open"), since subprocess.Popen would write directly to the underlying
                # file handle instead of using the "write" method of the Gzip object.
                # See https://stackoverflow.com/questions/7452427/
                # Thus, we need to handle two processes running in parallel.
                try:
                    compress_proc = subprocess.Popen(
                        ["gzip"],
                        cwd="/",
                        stdin=dump_proc.stdout,
                        stdout=dump_out,
                        stderr=subprocess.PIPE,
                    )
                except FileNotFoundError:
                    raise CommandError('executable "gzip" seems to be missing')
                # wait until either one process aborts or both succeed
                while not (
                    (compress_proc.returncode == 0) and (dump_proc.returncode == 0)
                ):
                    try:
                        if dump_proc.wait(0.1) != 0:
                            break
                    except subprocess.TimeoutExpired:
                        pass
                    try:
                        if compress_proc.wait(0.1) != 0:
                            break
                    except subprocess.TimeoutExpired:
                        pass
                # in case of failure: kill the other remaining process
                dump_proc.terminate()
                compress_proc.terminate()
                # check whether one of the processes failed (ignoring "None", due to "terminate")
                if (compress_proc.returncode is not None) and (
                    compress_proc.returncode != 0
                ):
                    # compression failed
                    error_message = compress_proc.stderr.read().decode()
                    raise CommandError(
                        "Failed to write compressed file: {}".format(error_message)
                    )
                if (dump_proc.returncode is not None) and (dump_proc.returncode != 0):
                    # database dump failed
                    error_message = dump_proc.stderr.read().decode()
                    raise CommandError(
                        "Failed to dump database via {}: {}".format(
                            dump_call[0], error_message
                        )
                    )
        except FileNotFoundError:
            raise CommandError(
                "Failed to create dump output file: {}".format(partial_output_filename)
            )
        except CommandError:
            os.unlink(partial_output_filename)
            raise
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
                'Successfully created database backup in "%s"' % partial_output_filename
            )
        )
