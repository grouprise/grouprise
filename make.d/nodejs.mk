BIN_NODE_SYSTEM = $(shell which nodejs node || true)
BIN_NODE ?= $(DIR_BUILD)/node/bin/node
BIN_NODE_PKG ?= $(DIR_BUILD)/node/bin/npm

NODE_VERSION = $(shell hash "$(BIN_NODE_SYSTEM)" 2>/dev/null && "$(BIN_NODE_SYSTEM)" -v || echo "v0.0.0")
NODE_VERSION_MIN = v8.12.0
NODE_URL_X86 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x86.tar.xz
NODE_URL_X64 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x64.tar.xz
NODE_URL = $(shell [ "$$(uname -m)" = "x86_64" ] && echo "$(NODE_URL_X64)" || echo "$(NODE_URL_X86)")
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
		ln -s "$$(which npm)" "$(NODE_LOCAL_DIR)/bin/npm"; \
	fi

$(BIN_NODE_PKG): $(BIN_NODE)
	@# verify that "npm" (BIN_NODE_PKG) is given as full path: node will not search PATH for it
	@[ -e "$(BIN_NODE_PKG)" ] || { echo >&2 "BIN_NODE_PKG must be a path (not an executable to be found via PATH)"; false; }
