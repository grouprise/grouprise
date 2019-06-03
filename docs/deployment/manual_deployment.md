# Manual Deployment

This guide describes the manual installation of *grouprise* using the sources.
Filesystem paths and some commands may be Debian specific but should be
easily adaptable to other Linux or BSD Distributions.


## Download the Sources

The latest stable release is available on
[git.hack-hro.de](https://git.hack-hro.de/stadtgestalten/stadtgestalten/tags), which
you can download as a zip or tar file (they all contain the same content).

Extract the file and place the content of the extracted directory
in `/usr/local/share/grouprise`.


## Install System Dependencies

Dependencies mentioned in this section refer to Debian package names, which
can be installed with `apt`. If you’re installating *grouprise* on an OS
other than Debian or one of its many derivates like Ubuntu, you have to find
the appropriate equivalents for your system’s package manager. A good starting
point may be the Debian [package search](https://www.debian.org/distrib/packages#search_packages)
that offers information about each package’s sources and website.

The following software is required when installing from sources:

* `make`
* `nodejs`
* `npm`
* `pip`
* `python3`
* `virtualenv`
* `wget`

We recommend a proper DBMS for running *grouprise*. Our recommendation is PostgreSQL, but
[any other option supported by Django](https://docs.djangoproject.com/en/2.2/ref/databases/)
should be fine too. Install the following packages for our recommendation:

* `postgresql`
* `python3-psycopg2`

Apart from that you’ll need an application server supporting the WSGI protocol
and a web server. Our recommendations are uWSGI and NGINX. We ship includable
configurations for both, so that any custom configuration is kept to a minimum.
Install the following packages for our recommendation:

* `nginx`
* `uwsgi`
* `uwsgi-plugin-python3`


## Additional System Dependencies and Functionality

Even though most of the application dependencies can be handled via the
virtualenv created in the section below, we recommend that you install
some of them with your systems package manager. Refer to the
[control](/debian/control) file for a list of packages. Everything starting
with `python3-` can and should be installed directly from the operating system.

This is not necessary but it is always a good idea to reduce the number of
manually installed and managed dependencies to increase overall security. Your
OS usually does a much better job at keeping dependencies up to date than a
single person ever could.

Some functionality requires additional packages. Those are:

* `python3-xapian` (for search)
* `redis-server` (for asynchronous mail-processing)


## Prepare Virtualenv and static Files

Unfortunately *grouprise* requires some libraries that are not available as
packages in Debian (and most likely other distributions). A virtualenv is a
simple way to install Python libraries without polluting directories that are
usually under control of the operating system and its package manager.

*grouprise* uses *Make* to ease these tasks for you. In order to create the
virtualenv and all other files necessary to run a proper *grouprise* instance
you’ll need to run the default make target in the directory *grouprise* was
installed in. If you’ve followed the defaults in the first step this should
come down too a few commands:

```bash
cd /usr/local/share/grouprise
make virtualenv_create
. build/venv/bin/activate
make
```


## Configuration

The what, how and why of *grouprise* configuration is outlined in the
[configuration documentation](./configuration.md), but you’ll need to create
a few files and symlinks to make it work.

1. Copy the `/usr/local/share/grouprise/grouprise/settings.py.production`
   file to `/usr/local/share/grouprise/grouprise/settings.py`. All application
   settings should be made there instead of `/etc/grouprise/settings.py`.
2. Copy `debian/grouprise.uwsgi.ini` to `/etc/uwsgi/apps-available/grouprise.ini`.
   Adapt the settings to your needs and symlink it to the `/etc/uwsgi/apps-enabled`
   directory.

You may also want to create a separate user and group for running grouprise and
set the corresponding `uid` setting in the uWSGI configuration.
