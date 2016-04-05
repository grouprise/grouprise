RM ?= rm -f
NPM_BIN ?= npm
NODE_BIN ?= $(shell which node nodejs)
GRUNT_BIN = node_modules/.bin/grunt


.PHONY: default clean

default: $(GRUNT_BIN)
	$(NPM_BIN) install
	$(NODE_BIN) $(GRUNT_BIN)

$(GRUNT_BIN):
	$(NPM_BIN) install

clean:
	$(RM) -r node_modules bower_components static
