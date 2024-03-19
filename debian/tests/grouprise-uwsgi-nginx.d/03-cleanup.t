#!/bin/sh
#
# clean up test environment

test_description="clean up test environment"

. /usr/share/sharness/sharness.sh


test_expect_success "stop nginx" '
  service nginx stop
'

test_expect_success "stop uwsgi" '
  service grouprise stop 2>&1 || { cat /var/log/grouprise/uwsgi.log; false; }
'

test_expect_success "stop postgresql database server" '
  service postgresql stop
'
test_done
