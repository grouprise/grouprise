# include this makefile snippet for automatic discovery of a:
#   * system-wide 'makefilet' installation (e.g. via the deb package)
#   * project-wide inclusion as a git-submodule (or code copy)
#   * on-demand download (temporarily stored in the local 'build/' directory)

# alternative version: "main" (the tip of the current development branch)
MAKEFILET_DOWNLOAD_VERSION ?= v0.14.2

ifneq ($(MAKEFILET_DOWNLOAD_URL_TEMPLATE),)
$(warning 'MAKEFILET_DOWNLOAD_URL_TEMPLATE' is deprecated. Use 'MAKEFILET_DOWNLOAD_URL_TEMPLATES' instead.)
MAKEFILET_DOWNLOAD_URL_TEMPLATES ?= $(MAKEFILET_DOWNLOAD_URL_TEMPLATE)
else
MAKEFILET_DOWNLOAD_URL_TEMPLATES ?= \
	https://notabug.org/sumpfralle/makefilet/archive/__VERSION__.tar.gz \
	https://git.hack-hro.de/kmohrf/makefilet/-/archive/__VERSION__/makefilet-__VERSION__.tar.gz
endif

ifneq ($(MAKEFILET_DOWNLOAD_URL),)
$(warning 'MAKEFILET_DOWNLOAD_URL' is deprecated. Use 'MAKEFILET_DOWNLOAD_URLS' instead.)
MAKEFILET_DOWNLOAD_URLS ?= $(MAKEFILET_DOWNLOAD_URL)
else
MAKEFILET_DOWNLOAD_URLS ?= $(foreach template,$(MAKEFILET_DOWNLOAD_URL_TEMPLATES),$(subst __VERSION__,$(MAKEFILET_DOWNLOAD_VERSION),$(template)))
endif

# first attempt: system-wide installation (e.g. deb package) or submodule of this project?
-include makefilet/main.mk
ifndef DIR_MAKEFILET
# we failed - it is not available globally or as a submodule
# second attempt: include a downloaded makefilet archive
DIR_BUILD ?= build
DIR_MAKEFILET_DOWNLOAD = $(DIR_BUILD)/makefilet
-include $(DIR_MAKEFILET_DOWNLOAD)/main.mk
ifndef DIR_MAKEFILET
# third attempt: download and extract a known release
$(info Downloading 'makefilet' ...)
$(shell mkdir -p "$(DIR_MAKEFILET_DOWNLOAD)" \
	&& for url in $(MAKEFILET_DOWNLOAD_URLS); do \
		printf >&2 "Trying to download 'makefilet' from $$url ... "; \
		if wget --quiet --output-document - "$$url"; then \
			echo >&2 "OK"; \
			break; \
		else \
			echo >&2 "failed"; \
		fi; \
	done | tar -xz -C "$(DIR_MAKEFILET_DOWNLOAD)" --strip-components=1 -f -)
# last include attempt
-include $(DIR_MAKEFILET_DOWNLOAD)/main.mk
ifndef DIR_MAKEFILET
$(error Failed to initialize 'makefilet'. It seems like it is neither installed system-wide, as a submodule or available via download.)
endif
endif
endif
