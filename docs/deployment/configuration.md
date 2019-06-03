# grouprise Configuration

This guide describes which parts of *grouprise* are configurable and
how they can be configured. It assumes that you’ve already installed
*grouprise* on the target host either via our
[deb repository](./deployment.md#installation-with-apt) or
[manually](./manual_deployment.md).


## Quick Steps

If you just want to get a working setup fast follow these steps:

1. Copy the `/etc/grouprise/settings.py.dist` file to `/etc/grouprise/settings.py`.
2. Define the variables outlined in the settings file header. At the very least
   these are `SECRET_KEY`, `ADMINS`, and `ALLOWED_HOSTS`.
   You should also consider to define the `DATABASES` variable as described in the
   [Django documentation](https://docs.djangoproject.com/en/2.2/ref/databases/)
   because switching the database at a later point can be a fairly complicated
   and error-prone process. See the [section on database configuration](#database-configuration)
   for more detailed information.
3. Initialize the database by running `stadtctl migrate`.
4. Symlink the `/etc/uwsgi/apps-available/grouprise.ini` file to
   `/etc/uwsgi/apps-enabled/grouprise.ini`.
5. Copy the `/usr/share/doc/grouprise/examples/nginx.conf` file to
   `/etc/nginx/sites-available/grouprise`, adapt the server name to your liking
   and symlink the file to `/etc/nginx/sites-enabled/grouprise`.
6. Restart the uWSGI and NGINX services with `service uwsgi restart` and
   `service nginx restart`.
7. Visit the hostname defined in 5.


## Database Configuration

We recommend PostgreSQL as DBMS, but Django – the underlying web-framework of *grouprise* -
supports [many other options](https://docs.djangoproject.com/en/2.2/ref/databases/).

As migrating data from one DBMS to the other is often difficult and error-prone you
should avoid it whenever possible. Make your decision and stick with it :).

We explicitly **DO NOT** recommend to use SQLite in production.

If you decide on using PostgreSQL you can execute the following lines as
`postgres` user after starting the `psql` SQL shell. If the `postgres` user
is not available on your system you should install the `postgresql` package.
In this example we use the `de_DE` locale which should be activated beforehand
by running `dpkg-reconfigure locales`.

```sql
CREATE USER grouprise WITH PASSWORD 'YOUR_CUSTOM_PASSWORD';
CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;
```

After that you can add the following lines to your `/etc/grouprise/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'localhost',
        'NAME': 'grouprise',
        'USER': 'grouprise',
        'PASSWORD': 'YOUR_CUSTOM_PASSWORD',
    }
}
```

If this is the first time you’ve configured the database now is the time
to run `stadtctl migrate` to initialize it. This will create the SQL schema
that grouprise needs in order to operate.


## Application Configuration

Application settings are managed in the `/etc/grouprise/settings.py` file, which does
not exist by default. Create it by copying the `/etc/grouprise/settings.py.dist` file.

TODO: add documentation for the various grouprise settings.


## WSGI-Application and Web-Server Configuration

Even though *grouprise* should run with any WSGI application server
and/or web server, uWSGI and NGINX are the options that we use ourselves
and are familiar with. This is the reason why we ship preconfigured uWSGI
and NGINX configuration files as part of the `grouprise` deb package.

Note: If you have experience with other WSGI application or web servers
and plan on using them with *grouprise* in a production environment,
feel free to submit a pull/merge request for documentation. We’ll gladly
add it and will try to get rid of any stumbling blocks that may interfere
with such a setup.

## uWSGI

uWSGI is an extensible WSGI server. We ship a default config as part of our
deb package and is located in `/etc/uwsgi/apps-available`. You can activate
it by creating a symlink to the `/etc/uwsgi/apps-enabled` directory.

If you want to use your own uWSGI configuration, but want to keep the
integration with the package, make sure the filename of the configuration
in `/etc/uwsgi/apps-enabled` is `grouprise.ini`.

In case you just want to override the number of workers and/or threads you
also can set the `GROUPRISE_UWSGI_WORKERS` and `GROUPRISE_UWSGI_THREADS`
environment variables in `/etc/default/uwsgi` and set them to any number
that fits your needs.

Once you’ve symlinked the *grouprise* config or created your own, you
can restart uWSGI with `service uwsgi reload`. Note that setting or
changing the aforementioned worker and thread environment variables will
likely require a `restart` instead of a `reload`.

## NGINX

If you plan on using NGINX install it now with `apt install nginx`.

We ship an includable default configuration as part of our deb package, which
is located in `/etc/nginx/snippets/grouprise.conf` and contains rules
for serving the app via uWSGI, static file handling for media and assets
files, sensible cache settings, and a maintenance fallback site.

Copy the example server configuration from `/usr/share/doc/grouprise/examples/nginx.conf` to
`/etc/nginx/sites-available/grouprise` and modify it to your needs. The
`include snippets/grouprise.conf` line to will import the default configuration.

After you’re done reload NGINX with `service nginx reload`.
