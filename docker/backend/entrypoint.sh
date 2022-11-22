#!/bin/sh

set -eu

_status() {
    printf "[grouprise-init] %s\n" "$1" >&2
}

_prep() {
    if [ -z "${GROUPRISE_DOCKER_NO_MIGRATE:-}" ]; then
        _status "Executing migrations..."
        chronic grouprisectl migrate --no-input --skip-checks
    fi

    if [ -z "${GROUPRISE_DOCKER_NO_COLLECTSTATIC:-}" ]; then
        _status "Reloading assets..."
        GROUPRISE_USER=root chronic grouprisectl collectstatic --no-input --skip-checks --clear
    fi

    chown -R _grouprise: /var/lib/grouprise
}

_show_config() {
    _status "Current configuration:"
    echo >&2
    grouprisectl grouprise_settings dump --skip-checks | sed 's/^/\t/'
    echo >&2
}

if [ "$1" = uwsgi ]; then
    _show_config
    _prep
    _status "Starting uWSGI..."
fi

exec "$@"
