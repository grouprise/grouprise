FROM git-registry.hack-hro.de:443/kmohrf/docker-recipes/debbuild:buster as build-deps
WORKDIR /usr/src/app
# Create a deb package that contains all the packages from our
# Build-Depends section in the source package. This way we don’t
# have to list our build dependencies multiple times and are
# able to keep them all in the debian/control file.
COPY ./debian debian
RUN mk-build-deps debian/control


FROM git-registry.hack-hro.de:443/kmohrf/docker-recipes/debbuild-python-webdev:buster
# Copy the created Build-Depends package from the last build stage,
# serve it via a local apt repo, and install it so that all build
# dependencies for our build are available.
ARG LOCALES
COPY --from=build-deps \
    /usr/src/app/grouprise-build-deps_*.deb \
    /srv/local-apt-repository/grouprise-build-deps.deb
RUN /usr/lib/local-apt-repository/rebuild && \
    apt-get --yes update && \
    apt-get --yes --target=buster-backports install grouprise-build-deps && \
    apt-get --yes clean
# compile locales required for example app configuration
RUN apt-get --yes install locales && \
    for locale in $LOCALES; do sed -i "s/^# $locale/$locale/g" /etc/locale.gen; done && \
    dpkg-reconfigure locales && \
    apt-get --yes clean
