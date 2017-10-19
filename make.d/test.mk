LINT_PKG_IGNORE_GLOBAL = -path "./debian/*" -o -path "./build/*" -o -path "./.pybuild/*" -o -path "./scripts/*" \
	-o -path "./.venv/*" -o -path "./gitlab-ci-build-venv/*"
LINT_PKG_PEP420 = $(shell find . -mindepth 2 -type f -name "*.py" -not \( $(LINT_PKG_IGNORE_GLOBAL) \) -print0 | \
	xargs -0 -n1 dirname | sort | uniq)

.PHONY: lint
lint: lint_js lint-python lint_packages

.PHONY: lint_js
lint_js: $(DIR_NODE)
	$(RUN_NODE) "$(BIN_NODE_PKG)" run lint

.PHONY: lint_packages
lint_packages:
	# setuptools’ find_packages() does not find PEP420 packages
	# we therefor forbid the use of PEP420 to ease automation
	# see: https://github.com/pypa/setuptools/issues/97
	@EXIT=0; for package in $(LINT_PKG_PEP420); do \
		if [ ! -f "$$package/__init__.py" ]; then \
			EXIT=1; \
			echo "missing __init__.py in $$package" >&2; \
		fi; \
	done && test "$$EXIT" = "0"
	@echo "OK"

.PHONY: test
test: lint test_js test_py

.PHONY: test_py
test_py: virtualenv_check
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
	STADTGESTALTEN_PRESET=test python manage.py test

.PHONY: test_js
test_js: $(DIR_NODE) lint_js
	$(RUN_NODE) "$(BIN_NODE_PKG)" run test
