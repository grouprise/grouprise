# when using virtualenv sys.real_prefix is set and we use the path to the python
# binary to determine the actual location of the virtualenv. In any other case
# we fallback to the VIRTUAL_ENV variable or the `.venv` directory
DIR_VIRTUALENV := $(shell echo "import sys; hasattr(sys, 'real_prefix') or sys.exit(1)" | python3 && \
	echo "$$(dirname "$$(dirname "$$(which python)")")" || echo "$${VIRTUAL_ENV:-"$(DIR_BUILD)/venv"}")
BIN_ACTIVATE = $(DIR_VIRTUALENV)/bin/activate
STAMP_VIRTUALENV = $(DIR_BUILD)/.stamp_virtualenv

$(BIN_ACTIVATE):
	virtualenv -p python3 "$(DIR_VIRTUALENV)"

.PHONY: virtualenv_check
virtualenv_check:
	@# this should fail if dependencies are missing or no virtualenv is active
	@STADTGESTALTEN_PRESET=packaging python3 manage.py check >/dev/null || ( \
		echo '' >&2; \
		echo '» Some stadtgestalten dependencies are missing' >&2; \
		echo '» You have two options:' >&2; \
		echo '»  1. Install dependencies system-wide. See the requirements.txt file.' >&2; \
		echo '»  2. Run "make virtualenv_create && . $(BIN_ACTIVATE)".' >&2; \
		exit 1; \
	)

$(STAMP_VIRTUALENV): requirements.txt
	pip3 install --upgrade pip
	pip3 install --upgrade -r requirements.txt
	find "$(DIR_VIRTUALENV)" -name no-global-site-packages.txt -delete
	mkdir -p "$(dir $(STAMP_VIRTUALENV))"
	touch "$(STAMP_VIRTUALENV)"

.PHONY: virtualenv_update
virtualenv_update: $(STAMP_VIRTUALENV)

.PHONY: virtualenv_create
virtualenv_create: $(BIN_ACTIVATE)
	( . "$(BIN_ACTIVATE)" && $(MAKE) virtualenv_update )
