BIN_NODE_SYSTEM = $(shell which nodejs node | head -1)
BIN_NPM_SYSTEM = $(shell which npm || true)
NODE_LOCAL_DIR = $(DIR_BUILD)/node
BIN_NODE ?= $(abspath $(NODE_LOCAL_DIR))/bin/node
BIN_NPM ?= $(abspath $(NODE_LOCAL_DIR))/bin/npm

NODE_VERSION_SYSTEM = $(shell if [ -n "$(BIN_NODE_SYSTEM)" ]; then "$(BIN_NODE_SYSTEM)" --version; else echo "v0.0.0"; fi)
NODE_VERSION_MIN = v8.12.0
NODE_URL_X86 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x86.tar.xz
NODE_URL_X64 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x64.tar.xz
NODE_URL = $(shell if [ "$(shell uname -m)" = "x86_64" ]; then echo "$(NODE_URL_X64)"; else echo "$(NODE_URL_X86)"; fi)

@# the module "phantomJS" fails to install without the environment setting OPENSSL_CONF
RUN_NODE = \
	PATH="$$PATH:$$(dirname "$(BIN_NODE)")" \
	DIR_BUILD="$(abspath $(DIR_BUILD))" \
	OPENSSL_CONF=/etc/ssl/ \
	"$(BIN_NODE)"


$(BIN_NODE):
	rm -rf "$(NODE_LOCAL_DIR)"
	mkdir -p "$(NODE_LOCAL_DIR)/bin"
	@if [ -z "$(BIN_NPM_SYSTEM)" ] || [ -z "$(BIN_NODE_SYSTEM)" ] || [ "$(NODE_VERSION_SYSTEM)" = "$$(printf '%s\n' "$(NODE_VERSION_SYSTEM)" "$(NODE_VERSION_MIN)" | sort -V | head -n1)" ]; then \
		if [ "$$(uname -s)" != "Linux" ]; then \
			echo >&2 "NodeJS download for non-linux platforms is sadly not supported. Please install $(NODE_VERSION_MIN) or later manually."; \
			exit 1; fi; \
		echo >&2 "Local nodejs version is missing or too old (before $(NODE_VERSION_MIN)) or 'npm' is missing. Downloading from server ..."; \
		if [ -n "$(shell which xzcat)" ]; then \
			wget -O - "$(NODE_URL)" | tar -xJ -C "$(NODE_LOCAL_DIR)" --strip-components=1 -f -; \
		else \
			echo >&2 "Failed to install nodejs due to missing dependency: xz compression tool (Debian: package 'xz-utils')"; \
		fi; \
	else \
		echo >&2 "Local nodejs version is sufficient. Symlinking executables ..."; \
		ln -s "$(BIN_NODE_SYSTEM)" "$(NODE_LOCAL_DIR)/bin/node"; \
		ln -s "$(BIN_NPM_SYSTEM)" "$(NODE_LOCAL_DIR)/bin/npm"; \
	fi

$(BIN_NPM): $(BIN_NODE)
	@# verify that "npm" (BIN_NPM) is given as full path: node will not search PATH for it
	@if [ -z "$(BIN_NPM)" ] || [ ! -x "$(BIN_NPM)" ]; then echo >&2 "BIN_NPM must be a path (not an executable to be found via PATH)"; exit 1; fi
