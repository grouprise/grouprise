# Quick Setup

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    
    npm install && node_modules/.bin/grunt

Visit http://localhost:8000/


# Release workflow

1. clean your workspace (the output of `git status` should be empty)
2. checkout the master branch and update it
3. run `make release-patch`, `make release-feature` or `make release-breaking`
4. describe your changes in the `git tag` message
5. in case of problems: discard your last commit and stop reading here
6. push your updated master branch (`git push ???`) and push the tags (`git push --tags`)
7. deploy the updated master branch on the target host: `make deploy-git`


# Local settings

Create a file `local_settings.py` and add all settings that you want to
override based on `stadt/settings.py`. The latter file imports all settings
from `local_settings.py` in case this file exists.


# Database setup

The preconfigured database is a local sqlite file.
For production deployment you should use a database server.

## PostgreSQL

The following statement creates a suitable database including proper collation settings:

    CREATE USER stadtgestalten with password 'PUT RANDOM NOISE';
    CREATE DATABASE stadtgestalten WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER stadtgestalten;

The above command requires the locale 'de_DE.UTF8' in the system of the database server.


# Production deployment
## UWSGI
The following uwsgi configuration is sufficient for running the software:

    [uwsgi]
    plugins = python3
    chdir = /srv/stadtgestalten/stadt
    file = wsgi.py
    touch-reload = /srv/stadtgestalten/local_settings.py
    touch-reload = settings.py
    virtualenv = /srv/virtualenvs/stadtgestalten
    pythonpath = /srv/stadtgestalten
    socket = /var/run/uwsgi/app/stadtgestalten/socket
    # anschalten fuer profiling
    #env = PROFILING_DIRECTORY=/tmp/profiling-stadtgestalten/
    # Switch to maintenance mode
    plugins = router_redirect
    # "touch-reload" for the offline-marker file is necessary, since "if-exists" is only processed
    # during startup (or reload).
    touch-reload = /srv/stadtgestalten/_OFFLINE_MARKER_UWSGI
    if-exists = /srv/stadtgestalten/_OFFLINE_MARKER_UWSGI
    route = .* redirect:https://offline.stadtgestalten.org/
    endif =
