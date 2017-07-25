DIR_STATIC = static
DIR_RES = res
DIR_LESS = $(DIR_RES)/less
DIR_JS = $(DIR_RES)/js
DIR_IMG = $(DIR_RES)/img
DIR_FONTS = $(DIR_RES)/fonts
DIR_NODE = node_modules
DIR_NODE_BIN ?= $(DIR_NODE)/.bin

BIN_YARN ?= yarn
BIN_NODE ?= node
BIN_STANDARD = $(DIR_NODE_BIN)/standard
BIN_POSTCSS = $(DIR_NODE_BIN)/postcss
BIN_LESSC = $(DIR_NODE_BIN)/lessc
BIN_WEBPACK = $(DIR_NODE_BIN)/webpack
BIN_SVGO = $(DIR_NODE_BIN)/svgo
BIN_FONTDUMP = $(DIR_NODE_BIN)/fontdump
BIN_MINIFY_JS = node -e "var fs = require('fs'); console.log(JSON.stringify(JSON.parse(fs.readFileSync('/dev/stdin', 'utf-8'))))"

DEPS_LESS = $(shell find "$(DIR_LESS)" -type f -name "*.less")
DEPS_JS = $(shell find "$(DIR_JS)" -type f -name "*.js")
DEPS_IMG = $(shell find "$(DIR_IMG)" -type f -not -name "*.svg")
DEPS_SVG = $(shell find "$(DIR_IMG)" -type f -name "*.svg")
DEPS_MANIFEST = $(DIR_RES)/config/manifest.json
DEPS_FONTS = $(shell find "$(DIR_FONTS)" -type f)

# intermediate build files
BUILD_FONT_GOOGLE = $(DIR_BUILD)/fonts/google
BUILD_CSS_APP = $(DIR_BUILD)/css/app_unprefixed.css

# static output files
STATIC_CSS_APP = $(DIR_BUILD)/static/css/app.css
STATIC_JS_APP = $(DIR_BUILD)/static/js/app.js
STATIC_FONT = $(DIR_BUILD)/static/fonts
STATIC_FONT_GOOGLE = $(STATIC_FONT)/google
STATIC_FONT_FONTAWESOME = $(STATIC_FONT)/font-awesome
STATIC_IMG = $(DIR_BUILD)/static/img
STATIC_CONFIG_MANIFEST = $(DIR_BUILD)/static/config/manifest.json

URL_FONT_GOOGLE = https://fonts.googleapis.com/css?family=Roboto+Slab:300,400,700|Roboto:300,400,400i,500,700

$(DIR_NODE): package.json
	@# in dh_auto_install yarn tries to create a cache folder in /usr/local/share/.cache
	@# this has something to do with the environment dh_auto_install creates
	@# so we call it with an empty environment to be on the safe side
	PATH="$$PATH" env -i yarn install --no-progress
	touch -c "$(DIR_NODE)"

$(STATIC_FONT_GOOGLE): $(DIR_NODE)
	mkdir -p "$(BUILD_FONT_GOOGLE)"
	$(BIN_FONTDUMP) --target-directory "$(BUILD_FONT_GOOGLE)" --web-directory "../fonts/google" "$(URL_FONT_GOOGLE)"
	mkdir -p "$(STATIC_FONT_GOOGLE)"
	rsync -a --exclude "*.css" "$(BUILD_FONT_GOOGLE)/" "$(STATIC_FONT_GOOGLE)"
	touch "$(STATIC_FONT_GOOGLE)"

$(STATIC_FONT_FONTAWESOME): $(DIR_NODE)
	mkdir -p "$(STATIC_FONT_FONTAWESOME)"
	rsync -a "$(DIR_NODE)/font-awesome/fonts/" "$(STATIC_FONT_FONTAWESOME)"
	touch "$(STATIC_FONT_FONTAWESOME)"

$(STATIC_FONT): $(DEPS_FONT)
	mkdir -p "$(STATIC_FONT)"
	rsync -a "$(DIR_FONTS)/" "$(STATIC_FONT)"
	touch "$(STATIC_FONT)"

$(STATIC_IMG): $(DIR_NODE) $(DEPS_IMG) $(DEPS_SVG)
	mkdir -p "$(STATIC_IMG)"
	rsync -a --exclude "*.svg" "$(DIR_IMG)/" "$(STATIC_IMG)"
	for svg in $(DEPS_SVG); do \
		echo "compressing svg '$$svg'"; \
		"$(BIN_SVGO)" --multipass --quiet \
			"$$svg" "$(STATIC_IMG)/$$(realpath --relative-to "$(DIR_IMG)" "$$svg")"; \
	done
	touch "$(STATIC_IMG)"

$(STATIC_CONFIG_MANIFEST): $(DEPS_MANIFEST)
	mkdir -p "$$(dirname "$(STATIC_CONFIG_MANIFEST)")"
	cat "$(DEPS_MANIFEST)" | $(BIN_MINIFY_JS) > "$(STATIC_CONFIG_MANIFEST)"

$(STATIC_CSS_APP): $(DIR_NODE) $(DEPS_LESS) $(BUILD_FONT_GOOGLE)
	NODE_ENV=production $(BIN_LESSC) --strict-math=on --strict-units=on "$(DIR_LESS)/app.less" "$(BUILD_CSS_APP)"
	NODE_ENV=production $(BIN_POSTCSS) --config postcss.config.js --output "$(STATIC_CSS_APP)" "$(BUILD_CSS_APP)"

$(STATIC_JS_APP): $(DIR_NODE) $(DEPS_JS)
	NODE_ENV=production $(BIN_WEBPACK) --bail

.PHONY: assets_fonts
assets_fonts: $(STATIC_FONT) $(STATIC_FONT_GOOGLE) $(STATIC_FONT_FONTAWESOME)

 .PHONY: assets_img
assets_img: $(STATIC_IMG)

.PHONY: assets_config
assets_config: $(STATIC_CONFIG_MANIFEST)

.PHONY: assets_css
assets_css: $(STATIC_CSS_APP)

.PHONY: assets_js
assets_js: $(STATIC_JS_APP)

.PHONY: assets
assets: assets_fonts assets_img assets_config assets_css assets_js
