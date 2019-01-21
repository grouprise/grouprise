import os
import datetime
from subprocess import check_call, check_output
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


def create_filename(directory, prefix, filename=None):
    return os.path.join(directory, '{prefix}{filename}'.format(**{
        'prefix': '{}_'.format(prefix) if prefix else '',
        'filename': filename or datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.sql'
    }))


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
    uri += '{}/{}'.format(host, name)
    return uri


class Command(BaseCommand):
    help = 'exports the currently configured database'

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='', help='prefix for the filename')
        parser.add_argument('--output-dir', default=settings.BACKUP_PATH,
                            help='backup storage dir')
        parser.add_argument('--output-file', default=None, help='backup filename')

    def handle(self, *args, **options):
        prefix = options.get('prefix')
        output_dir = options.get('output_dir')
        output_file = options.get('output_file')
        db = settings.DATABASES['default']
        engine = db['ENGINE'].split('.')[-1]
        file = create_filename(output_dir, prefix, output_file)

        if engine == 'sqlite3':
            try:
                dump = check_output(['sqlite3', db['NAME'], '.dump'])
                with open(file, 'wb') as dump_file:
                    dump_file.write(dump)
            except FileNotFoundError as err:
                if err.filename == 'sqlite3':
                    raise CommandError('missing the sqlite3 binary. please install it') from err
                else:
                    raise err
        elif engine == 'postgresql':
            try:
                check_call([
                    'pg_dump', '--no-owner', '--no-privileges', '--no-password', '-f', file,
                    create_psql_uri(db)
                ])
            except FileNotFoundError as err:
                raise CommandError('missing the pg_dump binary. please install it') from err
        else:
            raise CommandError('database backup not supported with %s engine' % engine)

        self.stdout.write(
            self.style.SUCCESS('Successfully created database backup in "%s"' % file)
        )
