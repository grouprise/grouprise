# Extract the list of debian packages in the Depends and Recommends sections
# of relevant grouprise packages
FROM debian:bullseye-slim AS grouprise-depends
RUN apt update -y && apt install -y dctrl-tools && apt-get clean -y
ADD debian/control ./
RUN for pkg in grouprise grouprise-db-postgresql; do \
      grep-dctrl --show-field=Depends,Recommends -P "$pkg" --exact-match control \
        | grep -E '^\s+' | awk '{$1=$1};1' | cut -d' ' -f1 | grep -v '^[$#]' | grep -Eo '[a-z0-9\._-]+' | grep -Ev '^grouprise(-|$)'; \
    done | sort | uniq >depends

# build assets
FROM node:lts-alpine AS grouprise-assets
WORKDIR /root/assets
ADD package.json package-lock.json ./
RUN ADBLOCK=true npm ci && npx browserslist@latest --update-db
ADD res/ ./res/
ADD .eslintrc.js webpack.config.js ./
RUN npm run build

# create app image
FROM debian:bullseye-backports
# install dependencies available in debian
COPY --from=grouprise-depends depends /tmp
RUN apt update -y && \
    apt install -y -t bullseye-backports \
      adduser \
      git \
      inotify-tools \
      locales \
      python3-pip \
      wget \
      $(cat /tmp/depends) && \
    apt-get clean -y

# configure locales
RUN printf 'en_US.UTF-8 UTF-8\nde_DE.UTF-8 UTF-8\n' >/etc/locale.gen && \
    locale-gen && \
    update-locale LANG=de_DE.UTF-8 LC_MESSAGES=en_US.UTF-8

# install custom dependencies not available in debian
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

# configure runtime environment
RUN adduser --force-badname --gecos '' --disabled-password --shell /bin/bash --home /var/lib/grouprise _grouprise
WORKDIR /var/lib/grouprise
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/grouprise-entrypoint.sh"]
CMD [ "uwsgi", \
    "--show-config", \
    "--master", \
    "--lazy-apps", \
    "--plugin", "python3", \
    "--socket", "0.0.0.0:8001", \
    "--http-socket", "0.0.0.0:8002", \
    "--uid", "_grouprise", \
    "--gid", "_grouprise", \
    "--module", "grouprise.wsgi:application", \
    "--touch-reload", "/etc/grouprise/conf.d", \
    "--static-map", "/static/=/var/lib/grouprise/static/", \
    "--static-map", "/media/=/var/lib/grouprise/media/", \
    "--attach-daemon", "/usr/local/bin/grouprise-conf-watcher.sh" \
]
ENV GROUPRISE_CONFIG=/etc/grouprise/conf.d/ \
    PYTHONPATH=/usr/share/grouprise/python-lib/ \
    # This one freaks out the docker parser when used in CMD.
    UWSGI_STATIC_EXPIRES_URI="/stadt/static/core/base/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|avif|webp|ico|woff|ttf|otf|svg|scss|map|txt) 315360000" \
    # We need an env var for this so common_settings.py knows it has to set HUEY["immediate"] = False.
    UWSGI_ATTACH_DAEMON="grouprisectl run_huey --skip-checks" \
    # Debian uWSGI doesn’t support these as CLI options.
    UWSGI_HTTP_AUTO_CHUNKED=1 \
    UWSGI_HTTP_KEEPALIVE=1 \
    UWSGI_WSGI_ENV_BEHAVIOUR=holy \
    # You might want to override the following env variables.
    UWSGI_WORKERS=2 \
    UWSGI_THREADS=4 \
    LANG=de_DE.UTF-8 \
    LC_MESSAGES=en_US.UTF-8

# copy project source files and base configuration
COPY grouprise/ /usr/share/grouprise/python-lib/grouprise/
COPY manage.py /usr/share/grouprise/
COPY --from=grouprise-assets \
    /root/assets/grouprise/core/templates/core/assets/_assets.html \
    /usr/share/grouprise/python-lib/grouprise/core/templates/core/assets/_assets.html
COPY --from=grouprise-assets \
    /root/assets/build/static/ \
    /usr/share/grouprise/python-lib/grouprise/core/static/core/base/
COPY debian/grouprisectl /usr/local/bin/
COPY docker/backend/conf-watcher.sh /usr/local/bin/grouprise-conf-watcher.sh
COPY docker/backend/entrypoint.sh /usr/local/bin/grouprise-entrypoint.sh
COPY docker/backend/config.base.yaml /etc/grouprise/conf.d/0-static/000-base.yaml
