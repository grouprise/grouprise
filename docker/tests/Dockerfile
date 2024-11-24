# The image specified in `DOCKER_IMAGE_RUNTIME` is used for the test environment.
# The build procedure should always run in the same image, that is used by our CI.
ARG DOCKER_IMAGE_RUNTIME=docker.io/debian:bookworm-slim
ARG DOCKER_IMAGE_EXTRA_DEPENDENCIES=

FROM docker.io/debian:bookworm-slim AS build-deps
RUN apt update -y \
    && apt upgrade -y \
    && apt install -y devscripts
ADD debian/control ./
RUN mk-build-deps control \
    && mv *.deb build-deps.deb


FROM $DOCKER_IMAGE_RUNTIME AS base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y \
    && apt upgrade -y \
    && apt install -y \
      gdebi-core \
      git \
      locales \
      make \
      nodejs npm \
      pipx \
      wget

# configure locales
RUN echo 'de_DE.UTF-8 UTF-8' >/etc/locale.gen \
    && locale-gen

RUN if [ -n "$DOCKER_IMAGE_EXTRA_DEPENDENCIES" ]; then apt-get install --yes $DOCKER_IMAGE_EXTRA_DEPENDENCIES; fi

# install project dependencies
COPY --from=build-deps build-deps.deb /tmp/build-deps.deb
RUN gdebi --non-interactive /tmp/build-deps.deb

# switch to working directory with appropriate permissions
RUN adduser --home /build --gecos '' build
USER build
# Somehow the `WORKDIR` below is not created with proper ownership (see `USER` above) when using
# docker for building the image.
# Maybe other container image builders create the WORKDIR with proper USER ownership without this
# manual `install` call.
RUN install --owner build -d /build/app
WORKDIR /build/app

# install asset dependencies
ADD --chown=build package.json package-lock.json ./
RUN ADBLOCK=true npm ci

# simulate project working dir
ADD --chown=build ./VERSION ./
RUN mkdir debian docs grouprise grouprise.conf.d grouprise-dev.conf.d media offline-website res

# install hatch
RUN pipx install hatch

# prepare virtualenv
ADD --chown=build pyproject.toml ./
RUN hatch env create

# force makefilet initialization
ADD --chown=build ./Makefile ./
ADD --chown=build ./make.d/ ./make.d/
RUN make help >/dev/null

# prepare project files
ADD --chown=build ./ ./
RUN rm -rf grouprise.conf.d/* && make app_local_settings
RUN rm -f grouprise/core/templates/core/assets/_assets.html && touch grouprise/core/templates/core/assets/_assets.html

FROM base AS test-python
# work-around common IPv6 problems in docker environments that occur when binding to localhost
ENV GROUPRISE_DEFAULT_LMTPD_HOST=127.0.0.1
ENTRYPOINT ["hatch", "run", "manage"]
CMD ["test", "--verbosity", "1"]
