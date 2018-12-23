CONFIG_APP_SETUP = stadt/settings/local.py

define APP_SETUP_CONFIG
from stadt.settings.default import *
from stadt.settings.development import *

SECRET_KEY = '$(shell echo "$$HOME$$(date)" | md5sum | cut -c-20)'
ALLOWED_HOSTS = ['stadtgestalten.org', 'localhost']
ADMINS = [
	('Admins', 'yourmailaddress@example.com'),
]
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365
ABOUT_GROUP_ID = 1

STATICFILES_DIRS = [
    ('stadt', os.path.join(BASE_DIR, '$(DIR_BUILD)', 'static')),
]

# optional: user ID to be used as virtual "author" for articles imported via feeds
#STADTGESTALTEN_FEEDS_IMPORTER_USER_ID = 1
endef
export APP_SETUP_CONFIG


$(CONFIG_APP_SETUP): $(MAKEFILES)
	echo "$$APP_SETUP_CONFIG" > "$(CONFIG_APP_SETUP)"

.PHONY: app_migrate
app_migrate: virtualenv_check
	$(PYTHON_BIN) manage.py migrate

.PHONY: app_run
app_run: virtualenv_check
	STADTGESTALTEN_PRESET=development $(PYTHON_BIN) manage.py runserver

.PHONY: app_collect_static
app_collect_static: virtualenv_check assets
	STADTGESTALTEN_PRESET=packaging python manage.py collectstatic --no-input

.PHONY: app_local_settings
app_local_settings: $(CONFIG_APP_SETUP)

.PHONY: app_setup
app_setup: $(CONFIG_APP_SETUP) $(BIN_ACTIVATE)
	( . "$(BIN_ACTIVATE)" && $(MAKE) virtualenv_update app_migrate app_collect_static app_run )
