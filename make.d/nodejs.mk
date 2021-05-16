BIN_NODE_SYSTEM = $(shell which nodejs node | head -1)
BIN_NPM_SYSTEM = $(shell which npm || true)
NODE_LOCAL_DIR = $(DIR_BUILD)/node
BIN_NODE_LOCAL = $(abspath $(NODE_LOCAL_DIR))/bin/node
BIN_NPM_LOCAL = $(abspath $(NODE_LOCAL_DIR))/bin/npm
BIN_NODE ?= $(shell if [ -e "$(BIN_NODE_LOCAL)" ]; then echo "$(BIN_NODE_LOCAL)"; else echo "$(BIN_NODE_SYSTEM)"; fi)
BIN_NPM ?= $(shell if [ -e "$(BIN_NPM_LOCAL)" ]; then echo "$(BIN_NPM_LOCAL)"; else echo "$(BIN_NPM_SYSTEM)"; fi)

# the module "phantomJS" fails to install without the environment setting OPENSSL_CONF
RUN_NODE = \
	PATH="$$PATH:$(NODE_LOCAL_DIR)/bin" \
	DIR_BUILD="$(abspath $(DIR_BUILD))" \
	OPENSSL_CONF=/etc/ssl/ \
	"$(BIN_NODE)"
