# grouprise

grouprise is a platform destined to encourage and enable social action and solidarity in the context of your city. Bildet Banden!

## Quick Setup

### For administrators
You may want to install the latest [release](./-/blob/main/docs/deployment/deb.md) or a [snapshot build](https://git.hack-hro.de/grouprise/grouprise/builds/artifacts/main/raw/build/debian/export/grouprise.deb?job=deb-package) as deb packages.

### For developers

The *local source* approach described below is suitable for developing the code of grouprise itself.
The *system in docker* approach is helpful for developing integrations with other packages (e.g. a mail server or matrix).

#### Local Source

1. You will need [virtualenv](https://virtualenv.pypa.io/en/stable/), [node](https://nodejs.org/en/), [python3](https://www.python.org/), [flake8](http://flake8.pycqa.org/en/latest/), [pip](https://pip.pypa.io/en/stable/) and [make](https://www.gnu.org/software/make/) to get started. If you have all of those, you may proceed :). Otherwise see *Dependencies* below.
2. Run `make app_run` and wait until you see something like `Starting development server at http://127.0.0.1:8000/`
3. Visit http://127.0.0.1:8000/

#### System in Docker

1. generate and run a docker image containing a prepared Debian Bullseye image. It is ready for installing
grouprise's [deb packages](./-/blob/main/docs/deployment/deb.md) from grouprise's apt repository
or for testing locally built deb packages:
```shell
make run-docker-deb-prepared
```
1. install released packages from the official apt repository or locally built deb packages:
```shell
# a) install released grouprise packages
apt install grouprise
# b) install locally built packages
dpkg -i /app/build/debian/grouprise_*.deb
```


## Dependencies

Depending on your distribution (we assume you’ll be using something like Linux here) the build dependencies of this project will be available via your package manager.


### Debian
```sh
apt install make nodejs npm python3 virtualenv python3-flake8 python3-pip python3-sphinx python3-recommonmark python3-xapian
```


### Arch Linux
```sh
pacman -Sy make nodejs npm python python-virtualenv flake8 python-pip python-sphinx python-recommonmark python-xapian
```


## Local Settings

Your local Django settings will be located in `grouprise.yaml`.
Run `make app_local_settings` to create a default configuration.


## Database Setup

The preconfigured database is a local sqlite file.
For production deployment you should use a database server.

### PostgreSQL

The following statement creates a suitable database including proper collation settings:

    CREATE USER grouprise WITH PASSWORD 'put random noise';
    CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;

The command above requires the locale `de_DE.UTF8` in the system of the database server.


## Production deployment

We recommend to use the provided deb package.
It contains an [nginx](nginx.org/) and [UWSGI](https://projects.unbit.it/uwsgi/) configuration.

See also [deb.md](./docs/deployment/deb.md).


## Contributing

The source code of grouprise itself is released under the [AGPL version 3 or later](LICENSE),
which is included in the [LICENSE](LICENSE) file.

See [CONTRIBUTING.md](./CONTRIBUTING.md)
