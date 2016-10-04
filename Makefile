RM ?= rm -f
NPM_BIN ?= npm
NODEJS_BIN ?= $(shell which node nodejs | head -1)
GRUNT_BIN = node_modules/.bin/grunt
VIRTUALENV_NAME ?= stadtgestalten
DJANGO_SETTINGS ?= stadt.prod_settings
VIRTUALENV_BASE ?= /srv/virtualenvs
BUILD_PATH ?= build
SOURCE_VIRTUALENV = . "$(VIRTUALENV_BASE)/$(VIRTUALENV_NAME)/bin/activate"
PYTHON_DIRS = content entities stadt features core utils
# uwsgi beobachtet diese Datei und schaltet bei ihrer Existenz in den Offline-Modus:
#   if-exists = _OFFLINE_MARKER_UWSGI
#   route = .* redirect:https://offline.stadtgestalten.org/
#   endif =
OFFLINE_MARKER_FILE = _OFFLINE_MARKER_UWSGI

# symlink magic for badly packaged dependencies using "node" explicitely
HELPER_BIN_PATH = $(BUILD_PATH)/helper-bin
HELPER_PATH_ENV = PATH=$(HELPER_BIN_PATH):$$PATH
NODEJS_SYMLINK = $(HELPER_BIN_PATH)/node

ASSET_VERSION_PATH = stadt/ASSET_VERSION

# in dieser Datei wird die Zeichenkette 'VERSION = "X.Y.Z"' erwartet
VERSION_FILE = stadt/__init__.py
# Auslesen der aktuellen Version und Hochzaehlen des gewaehlten Index (je nach Release-Stufe)
NEXT_RELEASE = $(shell (cat $(VERSION_FILE); echo "tokens = [int(v) for v in VERSION.split('.')]; tokens[$(RELEASE_INCREMENT_INDEX)] += 1; print('%d.%d.%d' % tuple(tokens))") | python)
GIT_RELEASE_TAG = v$(NEXT_RELEASE)


.PHONY: asset_version default clean deploy deploy-git release-breaking release-feature release-patch reload static update-virtualenv test

asset_version:
	git log --oneline res | head -n 1 | cut -f 1 -d " " > $(ASSET_VERSION_PATH)


default: $(GRUNT_BIN)
	($(HELPER_PATH_ENV); export PATH; $(NODEJS_BIN) $(GRUNT_BIN))

$(GRUNT_BIN): $(NODEJS_SYMLINK)
	($(HELPER_PATH_ENV); export PATH; $(NPM_BIN) install)

$(NODEJS_SYMLINK):
	mkdir -p "$(HELPER_BIN_PATH)"
	@[ -n "$(NODEJS_BIN)" ] || { echo >&2 "Requirement 'nodejs' is missing for build"; exit 1; }
	ln -s "$(NODEJS_BIN)" "$(NODEJS_SYMLINK)"

static:
	$(SOURCE_VIRTUALENV) && python manage.py collectstatic --no-input --settings "$(DJANGO_SETTINGS)"

reload:
	@# trigger UWSGI-Reload
	touch stadt/prod_settings.py

update-virtualenv:
	$(SOURCE_VIRTUALENV) && pip install -r requirements.txt
	$(SOURCE_VIRTUALENV) && python manage.py migrate --settings "$(DJANGO_SETTINGS)"

deploy:
	$(MAKE) asset_version
	$(MAKE) test
	touch $(OFFLINE_MARKER_FILE)
	$(MAKE) default
	$(MAKE) update-virtualenv
	$(MAKE) static
	$(MAKE) reload
	$(RM) $(OFFLINE_MARKER_FILE)

deploy-git:
	git pull
	$(MAKE) deploy

# Position der zu veraendernden Zahl in der Release-Nummer (X.Y.Z)
release-breaking: RELEASE_INCREMENT_INDEX=0
release-feature: RELEASE_INCREMENT_INDEX=1
release-patch: RELEASE_INCREMENT_INDEX=2

release-breaking release-feature release-patch:
	@if [ -n "$$(git status -s)" ]; then \
		printf >&2 "\n%s\n\n" "*** ERROR: The working directory needs to be clean for a release. ***"; \
		false; fi
	@if [ -n "$$(git tag -l | while read v; do [ "$$v" != "$(GIT_RELEASE_TAG)" ] || echo FOUND; done)" ]; then \
		printf >&2 "\n%s\n\n" "*** ERROR: There is already a git tag of the next version: $(NEXT_RELEASE). Use 'git tag -d $(GIT_RELEASE_TAG)' if know what you are doing."; \
		false; fi
	sed -i 's/^VERSION = .*/VERSION = "$(NEXT_RELEASE)"/' "$(VERSION_FILE)"
	git add "$(VERSION_FILE)"
	git commit -m "Release $(NEXT_RELEASE)"
	git tag -a "$(GIT_RELEASE_TAG)"

test:
	$(SOURCE_VIRTUALENV) && python -m flake8 $(PYTHON_DIRS) && python manage.py test

clean:
	$(RM) -r node_modules
	$(RM) -r bower_components
	$(RM) -r static
	$(RM) -r $(BUILD_PATH)
	$(RM) $(OFFLINE_MARKER_FILE)
