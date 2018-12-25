ifeq ($(DISABLE_CUSTOM_VIRTUALENV),1)
ACTIVATE_VIRTUALENV ?= /dev/null
else
# when using virtualenv sys.real_prefix is set and we use the path to the python
# binary to determine the actual location of the virtualenv. In any other case
# we fallback to the VIRTUAL_ENV variable or the `.venv` directory
DIR_VIRTUALENV := $(shell echo "import sys; hasattr(sys, 'real_prefix') or sys.exit(1)" | python3 && \
	echo "$$(dirname "$$(dirname "$$(which python)")")" || echo "$${VIRTUAL_ENV:-"$(DIR_BUILD)/venv"}")
ACTIVATE_VIRTUALENV ?= $(DIR_VIRTUALENV)/bin/activate

# automatically generate the virtual environment
virtualenv_check: virtualenv_update
endif

VIRTUALENV_CREATE_ARGUMENTS ?= --system-site-packages
STAMP_VIRTUALENV = $(DIR_BUILD)/.stamp_virtualenv

$(ACTIVATE_VIRTUALENV):
	virtualenv -p python3 $(VIRTUALENV_CREATE_ARGUMENTS) "$(DIR_VIRTUALENV)"

.PHONY: virtualenv_check
virtualenv_check: $(ACTIVATE_VIRTUALENV)
	@# this should fail if dependencies are missing or no virtualenv is active
	@( . "$(ACTIVATE_VIRTUALENV)" && STADTGESTALTEN_PRESET=packaging python3 manage.py check >/dev/null ) || ( \
		echo '' >&2; \
		echo '» Some stadtgestalten dependencies are missing' >&2; \
		echo '» You have two options:' >&2; \
		echo '»  1. Install dependencies system-wide. See the requirements.txt file.' >&2; \
		echo '»  2. Run "make virtualenv_update && . $(ACTIVATE_VIRTUALENV)".' >&2; \
		exit 1; \
	)

$(STAMP_VIRTUALENV): requirements.txt
	( . "$(ACTIVATE_VIRTUALENV)" && pip3 install --upgrade pip )
	( . "$(ACTIVATE_VIRTUALENV)" && pip3 install --upgrade -r requirements.txt )
	mkdir -p "$(dir $(STAMP_VIRTUALENV))"
	touch "$(STAMP_VIRTUALENV)"

.PHONY: virtualenv_update
virtualenv_update: $(STAMP_VIRTUALENV)
