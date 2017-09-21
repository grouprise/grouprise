DIR_INSTALL_ROOT ?= usr/share/stadtgestalten
FILE_VERSION_ASSET = ASSET_VERSION

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
	git log --oneline res | head -n 1 | cut -f 1 -d " " > "$(DESTDIR)/$(DIR_INSTALL_ROOT)/$(FILE_VERSION_ASSET)"
