BIN_NODE_SYSTEM = $(shell hash nodejs 2>/dev/null && echo nodejs || hash node 2>/dev/null && echo node)
BIN_NODE ?= $(DIR_BUILD)/node/bin/node
BIN_NODE_PKG ?= $(DIR_BUILD)/node/bin/npm

NODE_VERSION = $(shell hash "$(BIN_NODE_SYSTEM)" 2>/dev/null && "$(BIN_NODE_SYSTEM)" -v || echo "v0.0.0")
NODE_VERSION_MIN = v8.12.0
NODE_URL_X86 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x86.tar.xz
NODE_URL_X64 = https://nodejs.org/dist/$(NODE_VERSION_MIN)/node-$(NODE_VERSION_MIN)-linux-x64.tar.xz
NODE_URL = $(shell [ "$$(uname -m)" = "x86_64" ] && echo "$(NODE_URL_X64)" || echo "$(NODE_URL_X86)")
NODE_TMP = $(DIR_BUILD)/node_tmp
NODE_DEST = $(DIR_BUILD)/node

RUN_NODE = PATH="$$PATH:$$(dirname "$(BIN_NODE)")" DIR_BUILD="$(abspath $(DIR_BUILD))" node


$(BIN_NODE):
	rm -rf "$(NODE_DEST)"
	mkdir -p "$(NODE_DEST)/bin"
	@if [  "$(NODE_VERSION)" = $$(printf '%s\n' "$(NODE_VERSION)" "$(NODE_VERSION_MIN)" | sort -V | head -n1) ] || ! hash npm 2>/dev/null; then \
		if [ "$$(uname -s)" != "Linux" ]; then \
			echo >&2 "NodeJS download for non-linux platforms is sadly not supported. Please install $(NODE_VERSION_MIN) or later manually."; \
			exit 1; fi; \
		echo >&2 "Local nodejs version is too old (before $(NODE_VERSION_MIN)). Downloading from server ..."; \
		wget -O - "$(NODE_URL)" | tar -xJ -C "$(NODE_DEST)" --strip-components=1 -f -; \
	else \
		echo >&2 "Local nodejs version is sufficient. Symlinking executables ..."; \
		ln -s "$$(which "$(BIN_NODE_SYSTEM)")" "$(NODE_DEST)/bin/node"; \
		ln -s "$$(which npm)" "$(NODE_DEST)/bin/npm"; \
	fi
