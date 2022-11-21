#!/bin/sh

# The uWSGI --touch-reload option doesn’t support glob syntax
# or watches specified directories recursively, so we need to
# watch the directory contents ourselves.

set -eu

CONF_DIR=/etc/grouprise/conf.d/

inotifywait \
    --quiet \
    --monitor \
    --recursive \
    --format '%w' \
    --event create \
    --event move \
    --event delete \
    --event close_write \
    "$CONF_DIR" | while read -r filename; \
do
    if echo "$filename" | grep -q '\.yaml$'; then
        touch "$CONF_DIR"
    fi
done
