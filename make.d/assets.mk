DIR_STATIC = $(DIR_BUILD)/static
DIR_RES = res
DIR_FONTS = $(DIR_RES)/fonts
DIR_NODE = node_modules
DIR_NODE_BIN ?= $(DIR_NODE)/.bin
STAMP_NODE_MODULES = $(DIR_NODE)/.stamp-install

BIN_NPM ?= npm
BIN_WEBPACK = $(DIR_NODE_BIN)/webpack
BIN_FONTDUMP = $(DIR_NODE_BIN)/fontdump

DEPS_ASSETS = $(shell find "$(DIR_RES)" -type f)
DEPS_FONTS = $(shell find "$(DIR_FONTS)" -type f)

# google fonts
GOOGLE_FONTS_CSS = $(DIR_BUILD)/fonts/google/fonts.css
URL_FONT_GOOGLE = https://fonts.googleapis.com/css?family=Roboto+Slab:300,400,700|Roboto:300,400,400i,500,700

# static output files
STAMP_STATIC_WEBPACK = $(DIR_BUILD)/.static_webpack

$(STAMP_NODE_MODULES): package.json
	"$(BIN_NPM)" ci --no-progress
	touch "$(STAMP_NODE_MODULES)"

$(GOOGLE_FONTS_CSS): $(STAMP_NODE_MODULES)
	"$(BIN_FONTDUMP)" \
		--target-directory "$(dir $(GOOGLE_FONTS_CSS))" \
		--web-directory "." \
		"$(URL_FONT_GOOGLE)"

$(STAMP_STATIC_WEBPACK): $(GOOGLE_FONTS_CSS) $(DEPS_ASSETS) webpack.config.js
	mkdir -p "$(DIR_STATIC)"
	"$(BIN_NPM)" run build
	touch "$(STAMP_STATIC_WEBPACK)"

.PHONY: assets_fonts
assets_fonts: $(GOOGLE_FONTS_CSS)

.PHONY: assets_webpack
assets_webpack: $(STAMP_STATIC_WEBPACK)

.PHONY: assets
assets: assets_fonts assets_webpack
