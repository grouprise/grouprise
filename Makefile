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

# symlink magic for badly packaged dependencies using "node" explicitely
HELPER_BIN_PATH = $(BUILD_PATH)/helper-bin
HELPER_PATH_ENV = PATH=$(HELPER_BIN_PATH):$$PATH
NODEJS_SYMLINK = $(HELPER_BIN_PATH)/node

ASSET_VERSION_PATH = stadt/ASSET_VERSION


.PHONY: asset_version default clean deploy deploy-git reload static update-virtualenv test

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
	$(MAKE) default
	$(MAKE) update-virtualenv
	$(MAKE) static
	$(MAKE) reload

deploy-git:
	git pull
	$(MAKE) deploy

test:
	$(SOURCE_VIRTUALENV) && python -m flake8 $(PYTHON_DIRS) && python manage.py test

clean:
	$(RM) -r node_modules
	$(RM) -r bower_components
	$(RM) -r static
	$(RM) -r $(BUILD_PATH)
