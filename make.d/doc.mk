DIR_BUILD_DOC = $(abspath $(DIR_BUILD)/doc)
SPHINX_WANTED_FILE_EXTENSIONS = html js css png


.PHONY: doc
doc:
	$(MAKE) -C docs html "BUILDDIR=$(DIR_BUILD_DOC)"


build: doc


.PHONY: install-doc
install-doc: doc
	cd "$(DIR_BUILD_DOC)/html" \
		&& { find -type f -false $(patsubst %,-or -name "*.%",$(SPHINX_WANTED_FILE_EXTENSIONS)); find _static -type f; } \
			| sort | uniq | while read -r fname; do \
				install -D --target-directory "$(abspath $(DESTDIR))/usr/share/doc/grouprise/html/$$(dirname "$$fname")" "$$fname"; done


install: install-doc


.PHONY: clean-doc
clean-doc:
	$(RM) -r "$(DIR_BUILD_DOC)"


clean: clean-doc
