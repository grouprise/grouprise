DESTDIR ?= /
DIR_INSTALL_ROOT_RELATIVE ?= usr/share/stadtgestalten
DIR_INSTALL_STATIC ?= $(DESTDIR)/$(DIR_INSTALL_ROOT_RELATIVE)/static

PYTHON_INSTALL_ARGS = --root "$(DESTDIR)" \
	--install-lib="/$(DIR_INSTALL_ROOT_RELATIVE)" \
	--install-scripts="/$(DIR_INSTALL_ROOT_RELATIVE)" \
	--install-data="/$(DIR_INSTALL_ROOT_RELATIVE)"

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
