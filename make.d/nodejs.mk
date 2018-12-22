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

assets_node_download:
	rm -rf "$(NODE_DEST)"
	mkdir -p "$(NODE_TMP)" "$(NODE_DEST)"
	wget -O - "$(NODE_URL)" | tar xJ -C "$(NODE_TMP)" -f -
	rsync -a "$(NODE_TMP)/$$(basename -s ".tar.xz" "$(NODE_URL)")/" "$(NODE_DEST)"
	rm -rf "$(NODE_TMP)"

assets_node_system:
	rm -rf "$(NODE_DEST)"
	mkdir -p "$(NODE_DEST)/bin"
	ln -s "$$(which $(BIN_NODE_SYSTEM))" "$(NODE_DEST)/bin/node"
	ln -s "$$(which npm)" "$(NODE_DEST)/bin/npm"

$(BIN_NODE):
	@if [  "$(NODE_VERSION)" = $$(echo -e "$(NODE_VERSION)\n$(NODE_VERSION_MIN)" | sort -V | head -n1) ] || ! hash npm 2>/dev/null; then \
		echo "nodejs version is too old. downloading from server..."; \
		$(MAKE) assets_node_download; \
	else \
		echo "system nodejs version is sufficient. linking system files..."; \
		$(MAKE) assets_node_system; \
	fi
