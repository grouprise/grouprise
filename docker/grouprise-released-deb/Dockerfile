FROM debian:buster

# configure external apt repository and install packages
RUN apt-get update \
    && apt-get --yes install wget pwgen locales postgresql nginx-light \
    && wget -q -O /etc/apt/trusted.gpg.d/deb.grouprise.org.asc https://deb.grouprise.org/keys/repository.asc \
    && echo "deb https://deb.grouprise.org/ unstable main" >>/etc/apt/sources.list \
    && echo "deb http://deb.debian.org/debian buster-backports main" >>/etc/apt/sources.list \
    && apt-get update \
    && apt-get --yes install python3-django/buster-backports python3-django-filters/buster-backports \
    && apt-get --yes install grouprise

# configure locales
RUN sed -i -E "s/^# ((de_DE|en_US)\.UTF-8.*)$/\1/" /etc/locale.gen \
    && locale-gen

# initialize database
RUN service postgresql start \
    && db_password=$(pwgen 32 1) \
    && printf '%s\n' \
            "CREATE USER grouprise WITH PASSWORD '$db_password';" \
            "CREATE DATABASE grouprise WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER grouprise;" \
        | su -c psql postgres \
    && sed -i "s/'PASSWORD':.*$/'PASSWORD': '$db_password',/" /etc/grouprise/settings.py

# publish service
RUN ln -s ../apps-available/stadtgestalten.ini /etc/uwsgi/apps-enabled/ \
    && service uwsgi restart \
    && echo "server { include snippets/grouprise.conf; }" >/etc/nginx/sites-available/grouprise \
    && ln -s ../sites-available/grouprise /etc/nginx/sites-enabled/ \
    && rm -f /etc/nginx/sites-enabled/default \
    && nginx -s reload && service nginx restart
