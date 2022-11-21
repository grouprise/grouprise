# grouprise

grouprise is a platform destined to encourage and enable social action and solidarity in the context of your city. Bildet Banden!

## Quick Setup

### For administrators
You may want to install the latest [release](./-/blob/main/docs/deployment/deb.md) or a [snapshot build](https://git.hack-hro.de/grouprise/grouprise/builds/artifacts/main/raw/build/debian/export/grouprise.deb?job=deb-package) as deb packages.

### For developers

grouprise has become an application with a lot of integrations into other services
like mail and [matrix](https://matrix.org/) servers and depends on other services
like task queues in order to work properly.

If you are just starting out, we recommend to use docker-compose
to jump-start your development environment.

Once you’ve got to know the intricacies and details of grouprise you might
feel comfortable to run grouprise with more low-level tooling,
but feel free to point out shortcomings in our docker-compose setup,
so we can fix them.

#### Development with docker-compose

If you’re running Linux or BSD, your favorite distribution will most
likely have a package for docker-compose. In case it doesn’t or if you
use a different operating system like Windows or macOS please
refer to the [docker-compose install guide](https://docs.docker.com/compose/install/)
to get it up and running.

First create a copy of the default configuration.
This only needs to be done once.

```sh
cp grouprise-dev.conf.d/000-common.yaml grouprise.conf.d/
```

After that you should be able to start a development environment by
executing the following command:

```sh
COMPOSE_FILE=docker-compose.yml:docker-compose.dev.yml docker-compose up --build
```

Bootstrapping the environment will take quite some time on your first start,
but eventually you’ll see *Running* in the output and the output itself
becomes more colorful once the individual services are started.

A short while after that you can visit `http://localhost:8008` in your browser
of choice.

Things are not working? Come join us in our
[grouprise-dev chatroom](https://matrix.to/#/#grouprise-dev:systemausfall.org)!

Please note: Some settings like `database` or the `data_path` are overridden
or extended internally by the docker-compose setup. Changing them in your local
configuration won’t have any effect. You’ll see a dump of your entire
configuration as it is used by grouprise in the output of docker-compose
under the `grouprise-backend` prefix.

#### Development with low-level tooling

1. You will need [virtualenv](https://virtualenv.pypa.io/en/stable/),
   [node](https://nodejs.org/en/),
   [python3](https://www.python.org/),
   [flake8](http://flake8.pycqa.org/en/latest/),
   [pip](https://pip.pypa.io/en/stable/) and
   [make](https://www.gnu.org/software/make/) to get started.
   If you have all of those, you may proceed :).
   Otherwise, see *Low-level tooling dependencies* below.
2. Run `make assets` if you plan on working on the frontend
3. Run `make app_run` and wait until you see something like
   `Starting development server at http://127.0.0.1:8000/`
4. Visit http://127.0.0.1:8000/


## Local Settings

Your local Django settings will be located in `grouprise.yaml`.
Run `make app_local_settings` to create a default configuration.

PS: Don’t run `make app_local_settings` if you’re using docker-compose!

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


## Low-level tooling dependencies

Depending on your distribution (we assume you’ll be using something like Linux here) the build dependencies of this project will be available via your package manager.

### Debian
```sh
apt install make nodejs npm python3 virtualenv python3-flake8 python3-pip python3-sphinx python3-recommonmark python3-xapian
```

### Arch Linux
```sh
pacman -Sy make nodejs npm python python-virtualenv flake8 python-pip python-sphinx python-recommonmark python-xapian
```
