.PHONY: all format lint test tests integration_tests docker_tests help extended_tests all_tests

# Default target executed when no arguments are given to make.
all: help

# Define variables for test paths
UNIT_TEST_PATH = tests/unit_tests/
INTEGRATION_TEST_PATH = tests/integration_tests/
TEST_FILE ?= tests/

# Run all tests (both unit and integration)
tests test:
	@echo "Running all tests..."
	poetry run pytest \
		--verbose \
		--cov=langchain_salesforce \
		--cov-report=term-missing \
		$(TEST_FILE)

test_watch:
	poetry run ptw \
		--snapshot-update \
		--now . \
		-- -vv $(TEST_FILE)

# Run integration tests only
integration_test integration_tests:
	@echo "Running integration tests..."
	poetry run pytest \
		--verbose \
		--cov=langchain_salesforce \
		--cov-report=term-missing \
		$(INTEGRATION_TEST_PATH)

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python and notebook files.
PYTHON_FILES=.
MYPY_CACHE=.mypy_cache
lint format: PYTHON_FILES=.
lint_diff format_diff: PYTHON_FILES=$(shell git diff --relative=libs/partners/salesforce --name-only --diff-filter=d master | grep -E '\.py$$|\.ipynb$$')
lint_package: PYTHON_FILES=langchain_salesforce
lint_tests: PYTHON_FILES=tests
lint_tests: MYPY_CACHE=.mypy_cache_test

lint lint_diff lint_package lint_tests:
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff check $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff format $(PYTHON_FILES) --diff
	[ "$(PYTHON_FILES)" = "" ] || mkdir -p $(MYPY_CACHE) && poetry run mypy $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

format format_diff:
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff format $(PYTHON_FILES)
	[ "$(PYTHON_FILES)" = "" ] || poetry run ruff check --select I --fix $(PYTHON_FILES)

spell_check:
	poetry run codespell --toml pyproject.toml

spell_fix:
	poetry run codespell --toml pyproject.toml -w

check_imports: $(shell find langchain_salesforce -name '*.py')
	poetry run python ./scripts/check_imports.py $^

######################
# HELP
######################

help:
	@echo '----'
	@echo 'all_tests                    - run all unit and integration tests'
	@echo 'test                         - run unit tests'
	@echo 'tests                        - run unit tests'
	@echo 'integration_tests            - run integration tests'
	@echo 'test TEST_FILE=<test_file>   - run specific test file'
	@echo 'check_imports                - check imports'
	@echo 'format                       - run code formatters'
	@echo 'lint                         - run linters'
	@echo '----'
