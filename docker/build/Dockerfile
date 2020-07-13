FROM git-registry.hack-hro.de:443/kmohrf/docker-recipes/debbuild:buster as build-deps
WORKDIR /usr/src/app
# Create a deb package that contains all the packages from our
# Build-Depends section in the source package. This way we don’t
# have to list our build dependencies multiple times and are
# able to keep them all in the debian/control file.
COPY ./debian debian
RUN mk-build-deps debian/control


FROM git-registry.hack-hro.de:443/kmohrf/docker-recipes/debbuild-webdev:buster
# Copy the created Build-Depends package from the last build stage,
# serve it via a local apt repo, and install it so that all build
# dependencies for our build are available.
COPY --from=build-deps \
    /usr/src/app/grouprise-build-deps_*.deb \
    /srv/local-apt-repository/grouprise-build-deps.deb
RUN /usr/lib/local-apt-repository/rebuild && \
    apt update -y && \
    apt install -y -t buster-backports grouprise-build-deps && \
    apt-get clean -y

