#!/bin/sh
#
# Verify that the grouprise instance is reachable

test_description="verify the website"

. /usr/share/sharness/sharness.sh


test_expect_success "access website" '
  if response=$(curl --silent --show-error --fail http://'"$HTTP_SOCKET"'/); then
    printf "%s" "$response" | grep "<meta name=.application-name. content=.grouprise.>"
  else
    printf "Failure response received: %s\n" "$response"
    false
  fi
'

test_done
