DIR_STATIC = $(DIR_BUILD)/static
DIR_RES = res
DIR_FONTS = $(DIR_RES)/fonts
DIR_NODE = node_modules
DIR_NODE_BIN ?= $(DIR_NODE)/.bin

BIN_STANDARD = $(DIR_NODE_BIN)/standard
BIN_WEBPACK = $(DIR_NODE_BIN)/webpack
BIN_FONTDUMP = $(DIR_NODE_BIN)/fontdump

DEPS_ASSETS = $(shell find "$(DIR_RES)" -type f)
DEPS_FONTS = $(shell find "$(DIR_FONTS)" -type f)

# intermediate build files
BUILD_FONT_GOOGLE = $(DIR_BUILD)/fonts/google

# static output files
STATIC_FONT = $(DIR_BUILD)/static/fonts
STATIC_FONT_GOOGLE = $(STATIC_FONT)/google

URL_FONT_GOOGLE = https://fonts.googleapis.com/css?family=Roboto+Slab:300,400,700|Roboto:300,400,400i,500,700

$(DIR_NODE): $(BIN_NODE) package.json
	@# in dh_auto_install yarn tries to create a cache folder in /usr/local/share/.cache
	@# this has something to do with the environment dh_auto_install creates
	@# so we call it with an empty environment to be on the safe side
	env -i $(RUN_NODE) "$(BIN_NODE_PKG)" install --no-progress
	touch -c "$(DIR_NODE)"

$(STATIC_FONT_GOOGLE): $(DIR_NODE)
	mkdir -p "$(BUILD_FONT_GOOGLE)"
	$(RUN_NODE) "$(BIN_FONTDUMP)" --target-directory "$(BUILD_FONT_GOOGLE)" --web-directory "." "$(URL_FONT_GOOGLE)"
	mkdir -p "$(STATIC_FONT_GOOGLE)"
	rsync -a --exclude "*.css" "$(BUILD_FONT_GOOGLE)/" "$(STATIC_FONT_GOOGLE)"
	touch "$(STATIC_FONT_GOOGLE)"

$(DIR_STATIC): $(STATIC_FONT_GOOGLE) $(DEPS_ASSETS)
	NODE_ENV=production $(RUN_NODE) $(BIN_WEBPACK) --bail
	touch "$(DIR_STATIC)"

.PHONY: assets_fonts
assets_fonts: $(STATIC_FONT_GOOGLE)

.PHONY: assets_webpack
assets_webpack: $(DIR_STATIC)

.PHONY: assets
assets: assets_fonts assets_webpack
