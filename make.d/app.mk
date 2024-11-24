# This directory is configured via hatch as `GROUPRISE_CONFIG` in pyproject.toml.
CONFIG_APP_SETUP ?= grouprise.conf.d/
CONFIG_DEFAULT_SETUP ?= grouprise-dev.conf.d/


.PHONY: $(CONFIG_APP_SETUP)
$(CONFIG_APP_SETUP):
	if [ -z "$$(find "$(CONFIG_APP_SETUP)" -name '*.yaml')" ]; then \
		cp "$(CONFIG_DEFAULT_SETUP)"/*.yaml "$(CONFIG_APP_SETUP)/"; \
	fi

.PHONY: app_migrate
app_migrate: $(CONFIG_APP_SETUP)
	hatch run migrate

.PHONY: _app_run_single_job
_app_run_single_job: $(CONFIG_APP_SETUP)
	hatch run app

.PHONY: app_run
app_run: app_migrate app_collect_static app_compile_translations
	@# Parallel execution causes issues with interactive jobs, since these parallel processes
	@# are not connected to the terminal (and thus the process cannot detect the tty).
	@$(MAKE) --jobs=1 _app_run_single_job

.PHONY: app_collect_static
app_collect_static: $(CONFIG_APP_SETUP) assets
	hatch run collectstatic

.PHONY: app_compile_translations
app_compile_translations: PO_EDITOR=
app_compile_translations: django-translate

.PHONY: app_local_settings
app_local_settings: $(CONFIG_APP_SETUP)
