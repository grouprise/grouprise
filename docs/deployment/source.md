# Deployment from source

This guide describes the manual installation of *grouprise* using the sources.
Filesystem paths and some commands may be Debian-specific, but should be easily adaptable to other
Linux or unix-like distributions.


## Download the Sources

The latest stable release is available at
[git.hack-hro.de](https://git.hack-hro.de/grouprise/grouprise/-/tags).
You can download it as a `zip` or `tar` file (both containing the same content).

Extract the content of the archive into `/usr/local/share/grouprise`.


## Install System Dependencies

Dependencies mentioned in this section refer to Debian package names, which
can be installed with `apt`.
If you are installing *grouprise* on an operation system other than [Debian](https://debian.org/)
or one of its many derivatives (e.g. Ubuntu), then you have to find the appropriate equivalents for
your system’s package manager.
A good starting point may be the
[Debian package search](https://www.debian.org/distrib/packages#search_packages), which offers
information about each package’s sources and website.

The following software is required when installing from sources:

* `make`
* `nodejs`
* `npm`
* `pip`
* `python3`
* `virtualenv`
* `wget`

We recommend to pick a proper DBMS for running *grouprise*.
Our recommendation is PostgreSQL, but
[any other option supported by Django](https://docs.djangoproject.com/en/dev/ref/databases/)
should be fine too.
Install the following packages:

* `postgresql`
* `python3-psycopg2`

Apart from that you will need an application server supporting the WSGI protocol and a web server.
Our recommendations are [uWSGI](https://uwsgi-docs.readthedocs.io/) and
[NGINX](https://nginx.org/).
We ship configuration files for both, in order to minimize the required amount of customization.
Install the following packages:

* `nginx`
* `uwsgi`
* `uwsgi-plugin-python3`


## Additional System Dependencies and Functionality

Even though most of the application dependencies can be handled via the `virtualenv` created in the
section below, we recommend that you install some of these with your systems package manager.
Refer to the
[debian/control file](https://git.hack-hro.de/grouprise/grouprise/-/tree/main/debian/control)
for a list of packages.

All packages in the `Depends` section, whose names start with `python3-` can and should be
installed directly from the operating system.
This approach is not strictly necessary but it is always a good idea to reduce the number of
manually installed dependencies in order to increase overall security.
Your operating system ("distribution") usually does a much better job at keeping dependencies up to
date than a single person ever could.


## Prepare Virtualenv and Static Files

Unfortunately *grouprise* requires some libraries that are not available as packages in Debian (and
most likely other distributions).
A virtualenv is a simple way to install Python libraries without polluting directories that are
usually under control of the operating system and its package manager.

*grouprise* uses *Make* to ease these tasks for you.
In order to create the virtualenv and all other files necessary to run a proper *grouprise*
instance you will need to run the default make target in the directory *grouprise* was installed in.
If you have followed the defaults in the first step this should come down to a few commands:

```shell
cd /usr/local/share/grouprise
make virtualenv-update VIRTUALENV_CREATE_ARGUMENTS="--system-site-packages"
```


## Database Initialization and Configuration

See [database initialization](/administration/database/initialization) for details.


## Configure and Run *grouprise*

The what, how and why of *grouprise* configuration is outlined in the
[configuration documentation](/administration/configuration/index), but you will need to create a few
files and symlinks to make it work.


The *grouprise* process is managed via [uWSGI](https://uwsgi-docs.readthedocs.org/).

1. copy `grouprise.yaml.development` to `/etc/grouprise/conf.d/local.yaml` and adapt the settings
   according to your needs
    * add `debug: true`, if you run into problems later
1. create an uWSGI configuration (e.g. `/etc/grouprise/uwsgi.ini`)
    * see [debian/grouprise.uwsgi.ini](https://git.hack-hro.de/grouprise/grouprise/-/blob/main/debian/grouprise.uwsgi.ini)
1. create a systemd service for *grouprise*
    * see [debian/grouprise.service](https://git.hack-hro.de/grouprise/grouprise/-/blob/main/debian/grouprise.service)
    * alternative SysVinit script: [debian/grouprise.init](https://git.hack-hro.de/grouprise/grouprise/-/blob/main/debian/grouprise.init)
1. start the *grouprise* service: `service grouprise start`
1. create an nginx site configuration (e.g. `/etc/nginx/site-available/grouprise`):
    ```
    server {
        server_name YOUR_DOMAIN_NAME;
        client_max_body_size 10M;
        include /usr/local/share/grouprise/debian/nginx.conf;
    }
    ```
1. enable the site: `ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/`
1. restart nginx: `service nginx restart`
1. visit the fresh grouprise instance: `http://localhost/` (or use a suitable hostname)

You may also want to create a separate user and group for running *grouprise* and set the
corresponding `uid` setting in the uWSGI configuration.
