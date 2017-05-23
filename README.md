# Stadtgestalten

Stadtgestalten is a platform destined to encourage and enable social action and solidarity in the context of your city. Bildet Banden!

## Quick Setup

### For administrators
You may want to install the latest [snapshot build](wget https://git.hack-hro.de/stadtgestalten/stadtgestalten/builds/artifacts/master/raw/build/debian/export/stadtgestalten.deb?job=deb-package) as a deb package. Please note that this is a rather dirty package (only amd64, containing a virtualenv with python3.5 - suitable for Debian stretch).

### For developers
1. You will need [yarn](https://yarnpkg.com/lang/en/), [virtualenv](https://virtualenv.pypa.io/en/stable/), [node](https://nodejs.org/en/), [python3](https://www.python.org/), [flake8](http://flake8.pycqa.org/en/latest/), [pip](https://pip.pypa.io/en/stable/) and [make](https://www.gnu.org/software/make/) to get started. If you have all of those, you may proceed :). Otherwise see the Dependencies Section
2. Run `make app_setup` and wait until you see something like `Starting development server at http://127.0.0.1:8000/`
3. Visit http://127.0.0.1:8000/

## Dependencies

Depending on your distribution (we assume you’ll be using something like Linux here) the build dependencies of this project will be available via your package manager.

### Debian
For `virtualenv`, `python3`, `flake8` and `pip` use apt:
```sh
apt install make virtualenv python3 python3-flake8 python3-pip
```
`node` is available as `nodejs` and `nodejs-legacy` (please install both), but you’ll have to have Debian Stretch to get a node version that is going to work. The nodejs people also offer pre-packaged up to date builds [here](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions).
`yarn` is not yet available in Debian. Take a look at their [installation manual](https://yarnpkg.com/en/docs/install).

### Arch Linux
Fortunately all of the required packages are available via pacman.
```sh
pacman -Sy make nodejs yarn flake8 python python-virtualenv python-pip 
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

We recommend to use the provided debian package. It already comes with a UWSGI config.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)
