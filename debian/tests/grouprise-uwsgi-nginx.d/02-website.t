#!/bin/sh
#
# Verify that the grouprise instance is reachable

test_description="verify the website"

. /usr/share/sharness/sharness.sh


test_expect_success "access website" '
  curl --silent --show-error --fail http://'"$HTTP_SOCKET"'/ \
    | grep "<meta name=.application-name. content=.grouprise.>"
'

test_done
