#!/bin/sh
#
# Verify that the grouprise instance is reachable

test_description="verify the website"

. /usr/share/sharness/sharness.sh


test_expect_success "access website" '
  response_with_status=$(curl --silent --show-error --write-out "%{http_code}" http://'"$HTTP_SOCKET"'/)
  response=$(printf "%s" "$response_with_status" | sed \$d)
  http_status=$(printf "%s" "$response_with_status" | sed -n \$p)
  if [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
    printf "%s" "$response" | grep "<meta name=.application-name. content=.grouprise.>"
  else
    printf "Failure response received (HTTP-Status %d):\n%s\n" "$http_status" "$response"
    false
  fi
'

test_done
