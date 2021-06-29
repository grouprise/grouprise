#!/bin/sh
#
# Verify that the grouprise instance is reachable via nginx and uwsgi

test_description="configure grouprise for postgresql, uwsgi and nginx"

. /usr/share/sharness/sharness.sh


test_expect_success "configure grouprise locales" '
  sed -i -E "s/^# ((de_DE|en_US)\.UTF-8.*)$/\1/" /etc/locale.gen
  locale-gen
'

test_expect_success "start postgresql database server" '
  service postgresql start
'

test_expect_success "configure grouprise database" '
  db_password=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
  # configure database password
  printf "%s\n" \
    "engine: postgresql" \
    "host: localhost" \
    "name: grouprise" \
    "user: grouprise" \
    "password: \"$db_password\"" \
    | GROUPRISE_USER=root grouprisectl grouprise_settings set database
  # create database
  psql_command1="CREATE ROLE grouprise LOGIN PASSWORD '"'"'$db_password'"'"';"
  psql_command2="CREATE DATABASE grouprise OWNER grouprise;"
  psql_call="psql --echo-errors --command=\"$psql_command1\" --command=\"$psql_command2\""
  su -c "$psql_call" postgres
'

test_expect_success "configure grouprise proxy setup" '
  echo "- localhost" | GROUPRISE_USER=root grouprisectl grouprise_settings set extra_allowed_hosts
  echo "disabled" | GROUPRISE_USER=root grouprisectl grouprise_settings set transport_security
'

test_expect_success "configure nginx site" '
  cat >/etc/nginx/sites-enabled/grouprise <<EOF
server {
  listen '"$HTTP_SOCKET"';
  include snippets/grouprise.conf;
}
EOF
  # avoid using port 80 (only relevant if the test does not run in a separate network environment)
  rm -f /etc/nginx/sites-enabled/default
'

test_expect_success "restart nginx" '
  service nginx restart
'

test_expect_success "start grouprise" '
  # we cannot prevent uwsgi from emitting "getting INI configuration from ..." to stderr
  service grouprise start 2>&1
'

test_done
