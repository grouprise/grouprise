LINT_PKG_IGNORE_GLOBAL = -path "./debian/*" -o -path "./build/*" -o -path "./.pybuild/*" -o -path "./scripts/*" \
	-o -path "./.venv/*" -o -path "./gitlab-ci-build-venv/*" -o -path "./docs/*" -o -path "./venv/*"
LINT_PKG_PEP420 = $(shell find . -mindepth 2 -type f -name "*.py" -not \( $(LINT_PKG_IGNORE_GLOBAL) \) -print0 | \
	xargs -0 -n1 dirname | sort | uniq)
SPELLING_DIRECTORIES ?= debian docker docs grouprise make.d
SPELLING_IGNORE_FILE = .codespell-ignore-filenames
ASSETS_TEMPLATE = grouprise/core/templates/core/assets/_assets.html

CONTAINER_RUNNER = $(shell which docker podman | head -1)

.PHONY: lint
lint: lint_js lint_packages lint_spelling

.PHONY: lint_js
lint_js: $(STAMP_NODE_MODULES)
	"$(BIN_NPM)" run lint

.PHONY: lint_packages
lint_packages:
	# setuptools’ find_packages() does not find PEP420 packages
	# we therefore forbid the use of PEP420 to ease automation
	# see: https://github.com/pypa/setuptools/issues/97
	@EXIT=0; for package in $(LINT_PKG_PEP420); do \
		if [ ! -f "$$package/__init__.py" ]; then \
			EXIT=1; \
			echo "missing __init__.py in $$package" >&2; \
		fi; \
	done && test "$$EXIT" = "0"
	@echo "OK"

.PHONY: test
test: test_js

# these test targets are provided by makefilet
test-python: test_py_prepare
test-python-django: test_py_prepare

.PHONY: test_py_prepare
test_py_prepare: app_local_settings
	@# check for duplicate test method names that may overwrite each other
	@duplicate_function_names=$$(find . -mindepth 2 -type f -name tests.py -not \( $(LINT_PKG_IGNORE_GLOBAL) \) \
			| xargs grep -h "def test_" \
			| sed 's/^ \+def //g' | cut -f 1 -d "(" \
			| sort | uniq -d); \
		if [ -n "$$duplicate_function_names" ]; then \
			echo "[ERROR] non-unique test method names found:"; \
			echo "$$duplicate_function_names" | sed 's/^/    /g'; \
			exit 1; \
		fi >&2
	@# Our base template includes 'core/assets/_assets.html' which is generated by 'make assets'.
	@# Without it any view that renders from the base template will fail when the include
	@# is resolved, which breaks a lot of our python-tests. As this template only includes
	@# asset metadata and JavaScript & CSS file references, we simply make sure that the file
	@# exists during the test run. The content itself is of no relevance to the python-tests.
	test -f $(ASSETS_TEMPLATE) || ( mkdir -p $(dir $(ASSETS_TEMPLATE)) && touch $(ASSETS_TEMPLATE) )

.PHONY: _run-in-test-container
_run-in-test-container:
	@echo "NOTE: Initial test environment creation or regeneration after dependency updates might take a few minutes..." >&2
	$(CONTAINER_RUNNER) run --rm -it "$$($(CONTAINER_RUNNER) build --file ./docker/tests/Dockerfile --target "$(TARGET)" --quiet .)" $(COMMAND)

.PHONY: test-python-in-container
test-python-in-container:
	@$(MAKE) --no-print-directory --jobs=1 _run-in-test-container TARGET=test-python

.PHONY: test_js
test_js: $(STAMP_NODE_MODULES) lint_js
	"$(BIN_NPM)" run test

.PHONY: report-python-coverage
coverage_py: $(ACTIVATE_VIRTUALENV) $(VIRTUALENV_UPDATE_STAMP)
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" -m coverage run -m manage test )
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" -m coverage report )
	( . "$(ACTIVATE_VIRTUALENV)" && "$(PYTHON_BIN)" -m coverage html --directory="$(DIR_BUILD)/coverage-report" )
	@echo "Coverage Report Location: file://$(realpath $(DIR_BUILD))/coverage-report/index.html"

.PHONY: lint_spelling
lint_spelling:
	find $(SPELLING_DIRECTORIES) -type f -print0 \
		| grep --null-data --invert-match --line-regexp --fixed-strings --file=$(SPELLING_IGNORE_FILE) \
		| xargs --null --no-run-if-empty codespell --check-filenames
