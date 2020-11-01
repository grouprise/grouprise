DIR_BUILD_DOC = $(abspath $(DIR_BUILD)/doc)


.PHONY: doc
doc:
	$(MAKE) -C docs html "BUILDDIR=$(DIR_BUILD_DOC)"


build: doc


.PHONY: install-doc
install-doc: doc
	mkdir -p "$(DESTDIR)/usr/share/doc/grouprise/html"
	cp "$(DIR_BUILD_DOC)"/html/*.html \
		"$(DIR_BUILD_DOC)"/html/*.js \
		"$(DESTDIR)/usr/share/doc/grouprise/html/"
	cp -r "$(DIR_BUILD_DOC)"/html/configuration \
		"$(DIR_BUILD_DOC)"/html/database \
		"$(DIR_BUILD_DOC)"/html/_static \
		"$(DESTDIR)/usr/share/doc/grouprise/html/"


install: install-doc


.PHONY: clean-doc
clean-doc:
	$(RM) -r "$(DIR_BUILD_DOC)"


clean: clean-doc
