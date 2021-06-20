CONFIG_APP_SETUP = grouprise.yaml
CONFIG_APP_SETUP_TEMPLATE = grouprise.yaml.development


$(CONFIG_APP_SETUP): $(GROUPRISE_MAKEFILES)
	cp "$(CONFIG_APP_SETUP_TEMPLATE)" "$(CONFIG_APP_SETUP)"

.PHONY: app_migrate
app_migrate: virtualenv-check
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" manage.py migrate )

# makefilet runs "manage.py check" during "virtualenv-check" - thus we need the settings beforehand
virtualenv-check: app_local_settings

.PHONY: app_run
app_run: app_migrate app_collect_static app_compile_translations
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" manage.py runserver )

.PHONY: app_collect_static
app_collect_static: virtualenv-check assets
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" manage.py collectstatic --no-input )

.PHONY: app_local_settings
app_local_settings: $(CONFIG_APP_SETUP)

.PHONY: app_collect_translation_strings
app_collect_translation_strings:
	( . "$(ACTIVATE_VIRTUALENV)" && cd grouprise && "$(PYTHON_BIN)" ../manage.py makemessages --no-location )

.PHONY: app_compile_translations
app_compile_translations:
	( . "$(ACTIVATE_VIRTUALENV)" && cd grouprise && "$(PYTHON_BIN)" ../manage.py compilemessages )

.PHONY: app_translate
app_translate:
	$(MAKE) app_collect_translation_strings
	$(MAKE) app_compile_translations
