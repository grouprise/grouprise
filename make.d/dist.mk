DIR_INSTALL_ROOT ?= usr/share/stadtgestalten
DIR_INSTALL_STATIC ?= $(DIR_INSTALL_ROOT)/static

PYTHON_INSTALL_ARGS = --root "$(DESTDIR)" \
	--install-lib="/$(DIR_INSTALL_ROOT)" \
	--install-scripts="/$(DIR_INSTALL_ROOT)" \
	--install-data="/$(DIR_INSTALL_ROOT)"

.PHONY: clean-grouprise
clean-grouprise:
	$(RM) -r node_modules
	$(RM) -r static
	$(RM) -r $(DIR_BUILD)

clean: clean-grouprise

.PHONY: build-grouprise
build-grouprise: assets app_migrate app_collect_static
build: build-grouprise

.PHONY: install-grouprise
install-grouprise: build-grouprise
	mkdir -p "$(DIR_INSTALL_STATIC)"
	cp -r --target-directory="$(DIR_INSTALL_STATIC)/" "$(DIR_STATIC)"/*

install: install-grouprise
