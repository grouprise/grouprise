DIR_INSTALL_ROOT ?= usr/share/stadtgestalten

PYTHON_INSTALL_ARGS = --root "$(DESTDIR)" \
	--install-lib="/$(DIR_INSTALL_ROOT)" \
	--install-scripts="/$(DIR_INSTALL_ROOT)" \
	--install-data="/$(DIR_INSTALL_ROOT)"

.PHONY: clean
clean:
	$(RM) -r node_modules
	$(RM) -r static
	$(RM) -r $(DIR_BUILD)

.PHONY: build
build: assets app_collect_static

.PHONY: install
install: build
