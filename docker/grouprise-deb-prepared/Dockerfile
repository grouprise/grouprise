FROM debian:buster

# configure external apt repository and install packages
RUN apt-get update && \
    apt-get --yes install wget pwgen locales postgresql nginx-light && \
    wget -q -O /etc/apt/trusted.gpg.d/deb.grouprise.org.asc https://deb.grouprise.org/keys/repository.asc && \
    echo "deb https://deb.grouprise.org/ unstable main" >>/etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian buster-backports main" >>/etc/apt/sources.list && \
    apt-get update && \
    apt-get --yes install python3-django/buster-backports python3-django-filters/buster-backports

# Install all dependencies and recommends in order to simplify the manual installation of locally
# built packages (via dpkg instead of apt).
# TODO: enable the line below after switching to Debian Bullseye (apt v1.9 or newer is required)
#RUN apt-cache show grouprise | grep -E "^(Depends|Recommends):" | cut -f 2- -d " " | sed 's/, /\n/g' | tr '\n' '\0' | xargs --null --no-run-if-empty apt-get satisfy --yes
# the following (slightly hacky) command should be replaced with the one above in Debian Bullseye
RUN apt-cache show grouprise \
    | grep -E "^(Depends|Recommends):" \
    | cut -f 2- -d " " \
    | sed 's/, /\n/g' \
    | sed 's/ |.*$//g' \
    | sed 's/ (.*)$//g' \
    | tr '\n' '\0' \
    | xargs --null --no-run-if-empty apt-get install --yes

# configure locales
RUN sed -i -E "s/^# ((de_DE|en_US)\.UTF-8.*)$/\1/" /etc/locale.gen && \
    locale-gen

COPY grouprise-start-services /usr/bin/grouprise-start-services
