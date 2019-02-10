# grouprise

grouprise is a platform destined to encourage and enable social action and solidarity in the context of your city. Bildet Banden!

## Quick Setup

### For administrators
You may want to install the latest [snapshot build](https://git.hack-hro.de/stadtgestalten/stadtgestalten/builds/artifacts/master/raw/build/debian/export/stadtgestalten.deb?job=deb-package) as a deb package. Please note that this is a rather dirty package (embedded dependencies; suitable for Debian Stretch).

### For developers
1. You will need [virtualenv](https://virtualenv.pypa.io/en/stable/), [node](https://nodejs.org/en/) (downloaded automatically if unavailable), [python3](https://www.python.org/), [flake8](http://flake8.pycqa.org/en/latest/), [pip](https://pip.pypa.io/en/stable/) and [make](https://www.gnu.org/software/make/) to get started. If you have all of those, you may proceed :). Otherwise see the Dependencies Section
2. Run `make app_run` and wait until you see something like `Starting development server at http://127.0.0.1:8000/`
3. Visit http://127.0.0.1:8000/

## Dependencies

Depending on your distribution (we assume you’ll be using something like Linux here) the build dependencies of this project will be available via your package manager.

### Debian
For `virtualenv`, `python3`, `flake8` and `pip` use apt:
```sh
apt install make virtualenv python3 python3-flake8 python3-pip
```

Additionally `node` v8.12 or later and `npm` are required.  Both are available in Stretch-Backports and Buster.  If you do not have a suitable version installed, it will be automatically downloaded when running `make` (see `make.d/nodejs.mk`).

### Arch Linux
Fortunately all of the required packages are available via pacman.
```sh
pacman -Sy make nodejs npm flake8 python python-virtualenv python-pip
```


## Local Settings

Your local Django settings will be located in `stadt/settings/local.py`. Use `make app_local_settings` to create a default configuration. 


## Database Setup

The preconfigured database is a local sqlite file.
For production deployment you should use a database server.

### PostgreSQL

The following statement creates a suitable database including proper collation settings:

    CREATE USER stadtgestalten with password 'PUT RANDOM NOISE';
    CREATE DATABASE stadtgestalten WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER stadtgestalten;

The command above requires the locale 'de_DE.UTF8' in the system of the database server.


## Production deployment

We recommend to use the provided debian package. It contains a UWSGI and an nginx configuration file.

Necessary steps for running the software after package installation:

* install nginx and UWSGI (being remmomendations of the grouprise package): `apt install nginx uwsgi uwsgi-plugin-python3`
* enable the UWSGI service: `ln -s ../apps-available/grouprise.ini /etc/uwsgi/apps-enabled/`
* start UWSGI: `service uwsgi start`
* copy the nginx site example configuration: `cp /usr/share/doc/grouprise/examples/nginx.conf /etc/nginx/sites-available/grouprise`
* set a suitable `server_name`: `edit /etc/nginx/sites-available/grouprise`
    * or remove the `default` nginx site (if it is not in use) in order to let the `grouprise` site be picked irrespective of the requested hostname
* enable the site: `ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/`
* restart nginx: `service nginx restart`
* visit the fresh grouprise instance: `http://localhost/` (or use a suitable hostname)

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)
