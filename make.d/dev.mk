# used by makefilet
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
	@echo "    ci_image_build      - build docker image for CI"
	@echo "    ci_image_push       - push docker image for CI to docker registry"
	@echo "    ci_docker_login     - log into docker registry for CI images"
	@echo "    ci_docker_logout    - log out of docker registry (remove locally stored credentials)"
	@echo "    doc                 - build documentation"
	@echo "    install-grouprise   - install all grouprise components"
	@echo "    run-docker-deb-prepared  - enter a local docker instance prepared for installing deb packages"
	@echo "    tags                - generate tags file for grouprise code"
	@echo

help: help-grouprise


.PHONY: run-docker-deb-prepared
run-docker-deb-prepared:
	docker build --tag=grouprise-deb-prepared docker/grouprise-deb-prepared
	docker run \
		--tty \
		--interactive \
		--mount "type=bind,source=$$(pwd),destination=/app" \
		--publish 8000:80 \
		grouprise-deb-prepared "$$SHELL"
