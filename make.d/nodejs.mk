BIN_NODE_SYSTEM = $(shell which nodejs node || true)
BIN_NPM_SYSTEM = $(shell which npm || true)
BIN_NODE ?= $(DIR_BUILD)/node/bin/node
BIN_NPM ?= $(DIR_BUILD)/node/bin/npm

NODE_VERSION = $(shell if [ -n "$(BIN_NODE_SYSTEM)" ]; then "$(BIN_NODE_SYSTEM)" --version; else echo "v0.0.0"; fi)
NODE_VERSION_MIN = v8.12.0
NODE_URL_X86 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x86.tar.xz
NODE_URL_X64 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x64.tar.xz
NODE_URL = $(shell if [ "$(shell uname -m)" = "x86_64" ]; then echo "$(NODE_URL_X64)"; else echo "$(NODE_URL_X86)"; fi)
NODE_LOCAL_DIR = $(DIR_BUILD)/node

RUN_NODE = PATH="$$PATH:$$(dirname "$(BIN_NODE)")" DIR_BUILD="$(abspath $(DIR_BUILD))" node


$(BIN_NODE):
	rm -rf "$(NODE_LOCAL_DIR)"
	mkdir -p "$(NODE_LOCAL_DIR)/bin"
	@if [  "$(NODE_VERSION)" = $$(printf '%s\n' "$(NODE_VERSION)" "$(NODE_VERSION_MIN)" | sort -V | head -n1) ] || ! hash npm 2>/dev/null; then \
		if [ "$$(uname -s)" != "Linux" ]; then \
			echo >&2 "NodeJS download for non-linux platforms is sadly not supported. Please install $(NODE_VERSION_MIN) or later manually."; \
			exit 1; fi; \
		echo >&2 "Local nodejs version is too old (before $(NODE_VERSION_MIN)). Downloading from server ..."; \
		wget -O - "$(NODE_URL)" | tar -xJ -C "$(NODE_LOCAL_DIR)" --strip-components=1 -f -; \
	else \
		echo >&2 "Local nodejs version is sufficient. Symlinking executables ..."; \
		ln -s "$(BIN_NODE_SYSTEM)" "$(NODE_LOCAL_DIR)/bin/node"; \
		ln -s "$(BIN_NPM_SYSTEM)" "$(NODE_LOCAL_DIR)/bin/npm"; \
	fi

$(BIN_NPM): $(BIN_NODE)
	@# verify that "npm" (BIN_NPM) is given as full path: node will not search PATH for it
	@if [ -z "$(BIN_NPM)" ] || [ ! -x "$(BIN_NPM)" ]; then echo >&2 "BIN_NPM must be a path (not an executable to be found via PATH)"; exit 1; fi
