RM ?= rm -f
NPM_BIN ?= npm
NODEJS_BIN ?= $(shell which node nodejs | head -1)
GRUNT_BIN = node_modules/.bin/grunt
BUILD_PATH ?= build
BACKUP_PATH ?= backup
PYTHON_DIRS = content entities stadt features core utils
# uwsgi beobachtet diese Datei und schaltet bei ihrer Existenz in den Offline-Modus:
#   if-exists = _OFFLINE_MARKER_UWSGI
#   route = .* redirect:https://offline.stadtgestalten.org/
#   endif =
OFFLINE_MARKER_FILE = _OFFLINE_MARKER_UWSGI

DJANGO_SETTINGS_MODULE ?= stadt.settings

DB_CONNECTION_BACKUP ?= $(shell (echo "from $(DJANGO_SETTINGS_MODULE) import *; d=DATABASES['default']; format_string = {'sqlite3': 'echo .backup $(DB_BACKUP_FILE) | sqlite3 {NAME}', 'postgresql': 'pg_dump \"postgresql://{USER}:{PASSWORD}@{HOST}/{NAME}\" >$(DB_BACKUP_FILE)'}[d['ENGINE'].split('.')[-1]]; print(format_string.format(**DATABASES['default']))") | PYTHONPATH=. python)
DB_CONNECTION_RESTORE ?= $(shell (echo "from $(DJANGO_SETTINGS_MODULE) import *; d=DATABASES['default']; format_string = {'sqlite3': 'echo .restore $(DB_BACKUP_FILE) | sqlite3 {NAME}', 'postgresql': 'psql \"postgresql://{USER}:{PASSWORD}@{HOST}/{NAME}\" <$(DB_RESTORE_DATAFILE)'}[d['ENGINE'].split('.')[-1]]; print(format_string.format(**DATABASES['default']))") | PYTHONPATH=. python)
DB_BACKUP_FILE ?= $(BACKUP_PATH)/data-$(shell date +%Y%m%d%H%M).db

# symlink magic for badly packaged dependencies using "node" explicitly
HELPER_BIN_PATH = $(BUILD_PATH)/helper-bin
HELPER_PATH_ENV = PATH=$(HELPER_BIN_PATH):$$PATH
NODEJS_SYMLINK = $(HELPER_BIN_PATH)/node

ASSET_VERSION_PATH = stadt/ASSET_VERSION

# in dieser Datei wird die Zeichenkette 'VERSION = "X.Y.Z"' erwartet
VERSION_FILE = package.json
# Auslesen der aktuellen Version und Hochzaehlen des gewaehlten Index (je nach Release-Stufe)
NEXT_RELEASE = $(shell PYTHONPATH=. python -c "import stadt.version; print(stadt.version.$(RELEASE_INCREMENT_FUNCTION)())")
GIT_RELEASE_TAG = v$(NEXT_RELEASE)


.PHONY: asset_version check-virtualenv clean database-backup database-restore \
	default deploy deploy-git release-breaking release-feature \
	release-patch reload static update-virtualenv test website-offline \
	website-online

asset_version:
	git log --oneline res | head -n 1 | cut -f 1 -d " " > $(ASSET_VERSION_PATH)

database-backup:
	@mkdir -p "$(BACKUP_PATH)"
	$(DB_CONNECTION_BACKUP)

database-restore:
	@if [ -z "$$DB_RESTORE_DATAFILE" ]; then \
		echo >&2 "ERROR: You need to specify the source data file location (DB_RESTORE_DATAFILE=???)"; \
		exit 1; fi
	$(DB_CONNECTION_RESTORE)

default: $(GRUNT_BIN)
	($(HELPER_PATH_ENV); export PATH; $(NODEJS_BIN) $(GRUNT_BIN))

$(GRUNT_BIN): $(NODEJS_SYMLINK)
	($(HELPER_PATH_ENV); export PATH; $(NPM_BIN) install)

$(NODEJS_SYMLINK):
	mkdir -p "$(HELPER_BIN_PATH)"
	@[ -n "$(NODEJS_BIN)" ] || { echo >&2 "Requirement 'nodejs' is missing for build"; exit 1; }
	ln -s "$(NODEJS_BIN)" "$(NODEJS_SYMLINK)"

static: check-virtualenv
	python manage.py collectstatic --no-input

reload:
	@# trigger UWSGI-Reload
	touch "$$(echo "$(DJANGO_SETTINGS_MODULE)" | tr '.' '/').py"

website-offline:
	touch $(OFFLINE_MARKER_FILE)

website-online:
	$(RM) $(OFFLINE_MARKER_FILE)

check-virtualenv:
	@# this should fail if dependencies are missing or no virtualenv is active
	python manage.py check

update-virtualenv: check-virtualenv
	pip install -r requirements.txt
	python manage.py migrate

deploy:
	$(MAKE) asset_version
	$(MAKE) test
	$(MAKE) website-offline
	$(MAKE) database-backup
	$(MAKE) default
	$(MAKE) update-virtualenv
	$(MAKE) static
	# in "website-online" ist ein "reload" enthalten
	$(MAKE) website-online

deploy-git:
	git pull
	$(MAKE) deploy

# Position der zu veraendernden Zahl in der Release-Nummer (X.Y.Z)
release-breaking: RELEASE_INCREMENT_FUNCTION=get_next_breaking_version
release-feature: RELEASE_INCREMENT_FUNCTION=get_next_feature_version
release-patch: RELEASE_INCREMENT_FUNCTION=get_next_patch_version

release-breaking release-feature release-patch:
	@if [ -n "$$(git status -s)" ]; then \
		printf >&2 "\n%s\n\n" "*** ERROR: The working directory needs to be clean for a release. ***"; \
		false; fi
	@if [ -n "$$(git tag -l | while read v; do [ "$$v" != "$(GIT_RELEASE_TAG)" ] || echo FOUND; done)" ]; then \
		printf >&2 "\n%s\n\n" "*** ERROR: There is already a git tag of the next version: $(NEXT_RELEASE). Use 'git tag -d $(GIT_RELEASE_TAG)' if know what you are doing."; \
		false; fi
	# we rely on the specific formatting of this line in 'package.json'
	sed -i 's/"version": .*/"version": "$(NEXT_RELEASE)",/' "$(VERSION_FILE)"
	git add "$(VERSION_FILE)"
	git commit -m "Release $(NEXT_RELEASE)"
	git tag -a "$(GIT_RELEASE_TAG)"

test: check-virtualenv
	python -m flake8 $(PYTHON_DIRS)
	@# Die Umgebungsvariable "STADTGESTALTEN_IN_TEST" kann in "local_settings.py" geprueft
	@# werden, um die Verwendung einer postgres/mysql-Datenbankverbindung ohne "create"-Rechte
	@# zu verhindern. Mit sqlite klappen die Tests dann natuerlich.
	STADTGESTALTEN_IN_TEST=1 python manage.py test

clean:
	$(RM) -r node_modules
	$(RM) -r bower_components
	$(RM) -r static
	$(RM) -r $(BUILD_PATH)
	$(RM) $(OFFLINE_MARKER_FILE)
