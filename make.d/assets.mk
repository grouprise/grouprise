DIR_STATIC = $(DIR_BUILD)/static
DIR_RES = res
DIR_NODE = node_modules
STAMP_NODE_MODULES = $(DIR_NODE)/.stamp-install

BIN_NPM ?= npm

DEPS_ASSETS = $(shell find "$(DIR_RES)" -type f)

# static output files
STAMP_STATIC_WEBPACK = $(DIR_BUILD)/.static_webpack

$(STAMP_NODE_MODULES): package.json
	"$(BIN_NPM)" ci --no-progress
	touch "$(STAMP_NODE_MODULES)"


$(STAMP_STATIC_WEBPACK): $(DEPS_ASSETS) $(STAMP_NODE_MODULES) webpack.config.js
	mkdir -p "$(DIR_STATIC)"
	"$(BIN_NPM)" run build
	touch "$(STAMP_STATIC_WEBPACK)"


.PHONY: assets_webpack
assets_webpack: $(STAMP_STATIC_WEBPACK)

.PHONY: assets
assets: assets_webpack
