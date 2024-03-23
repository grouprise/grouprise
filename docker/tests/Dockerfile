FROM docker.io/debian:bookworm-slim AS build-deps
RUN apt update -y \
    && apt upgrade -y \
    && apt install -y devscripts
ADD debian/control ./
RUN mk-build-deps control \
    && mv *.deb build-deps.deb


FROM docker.io/debian:bookworm-slim AS base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y \
    && apt upgrade -y \
    && apt install -y \
      gdebi-core \
      git \
      locales \
      make \
      nodejs npm \
      python3-pip \
      python3-venv \
      wget

# configure locales
RUN echo 'de_DE.UTF-8 UTF-8' >/etc/locale.gen \
    && locale-gen

# install project dependencies
COPY --from=build-deps build-deps.deb /tmp/build-deps.deb
RUN gdebi --non-interactive /tmp/build-deps.deb
ADD ./docker/tests/venv-python /usr/local/bin/

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

# prepare virtualenv
ENV VIRTUAL_ENV=/build/venv
ADD --chown=build requirements.txt ./
RUN python3 -m venv --system-site-packages "$VIRTUAL_ENV" \
    && "$VIRTUAL_ENV/bin/pip3" install -r requirements.txt

# force makefilet initialization
ADD --chown=build ./Makefile ./
ADD --chown=build ./make.d/ ./make.d/
RUN make help >/dev/null

# prepare project files
ADD --chown=build ./ ./
RUN rm -rf grouprise.conf.d/* && make app_local_settings
RUN rm -f grouprise/core/templates/core/assets/_assets.html && touch grouprise/core/templates/core/assets/_assets.html

FROM base AS test-python
ENV GROUPRISE_LMTPD_HOST=127.0.0.1
ENTRYPOINT ["/usr/local/bin/venv-python", "manage.py"]
CMD ["test", "--verbosity", "1"]
