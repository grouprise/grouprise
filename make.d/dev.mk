TAGS_SOURCE_DIRS = account content core entities features stadt utils


.PHONY: help-grouprise
help-grouprise:
	@echo "Grouprise app targets:"
	@echo "    app_collect_static  - copy assets to django's static directory"
	@echo "    app_local_settings  - generate a local django configuration file"
	@echo "    app_migrate         - run django migrations for a local setup"
	@echo "    app_run             - run django server locally"
	@echo "    assets              - build assets (fonts and webpack)"
	@echo "    assets_fonts        - build font assets"
	@echo "    assets_webpack      - build webpack assets"
	@echo "    build-grouprise     - build all grouprise components"
	@echo "    clean-grouprise     - delete all built grouprise components"
	@echo "    doc                 - build documentation"
	@echo "    install-grouprise   - install all grouprise components"
	@echo "    tags                - generate tags file for grouprise code"
	@echo

help: help-grouprise
