import getpass
import datetime
import gzip
import os
from subprocess import check_call, CalledProcessError
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


def create_filename(directory, prefix, filename=None, suffix=''):
    return os.path.abspath(os.path.join(directory, '{prefix}{filename}{suffix}'.format(**{
        'prefix': '{}_'.format(prefix) if prefix else '',
        'filename': filename or datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.sql',
        'suffix': suffix,
    })))


def d(dict, key, default=None):
    try:
        value = dict[key]
        return value if value else default
    except KeyError:
        return default


def create_psql_uri(db):
    uri = 'postgresql://'
    user = d(db, 'USER', False)
    password = d(db, 'PASSWORD', False)
    host = d(db, 'HOST', 'localhost')
    name = d(db, 'NAME')
    if user and password:
        uri += '{}:{}@'.format(user, password)
    elif user:
        uri += '{}@'.format(user)
    elif host == 'localhost' and password is False:
        if user is False or user == getpass.getuser():
            # the database is on this host, no password was set
            # and either no user was set or the command runs as the defined user
            # this probably means that we postgres' username-matching
            # authentication mechanism
            return name
    uri += '{}/{}'.format(host, name)
    return uri


class Command(BaseCommand):
    help = 'exports the currently configured database'

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='', help='prefix for the filename')
        parser.add_argument('--output-dir', default=settings.GROUPRISE.get("BACKUP_PATH", "."),
                            help='backup storage dir')
        parser.add_argument('--output-file', default=None, help='backup filename')

    def handle(self, *args, **options):
        prefix = options.get('prefix')
        output_dir = options.get('output_dir')
        output_file = options.get('output_file')
        db = settings.DATABASES['default']
        engine = db['ENGINE'].split('.')[-1]
        output_filename = create_filename(output_dir, prefix, output_file, suffix=".gz")

        if engine == 'sqlite3':
            try:
                output_file = gzip.GzipFile(output_filename, 'wb')
            except FileNotFoundError as err:
                raise CommandError('Failed to create dump output file: {}'
                                   .format(output_filename)) from err
            try:
                check_call(['sqlite3', db['NAME'], '.dump'], stdout=output_file)
            except (FileNotFoundError, CalledProcessError) as err:
                output_file.close()
                os.unlink(output_filename)
                if isinstance(err, FileNotFoundError):
                    raise CommandError('missing the sqlite3 binary. please install it') from err
                else:
                    raise CommandError('Failed to create database dump.') from err
        elif engine in {'postgresql', 'postgis'}:
            try:
                check_call(['pg_dump', '--no-owner', '--no-privileges', '--compress=9',
                            '--file', output_filename, create_psql_uri(db)], cwd="/")
            except FileNotFoundError as err:
                raise CommandError('missing the pg_dump binary. please install it') from err
        else:
            raise CommandError('database backup not supported with %s engine' % engine)

        self.stdout.write(
            self.style.SUCCESS('Successfully created database backup in "%s"' % output_filename)
        )
