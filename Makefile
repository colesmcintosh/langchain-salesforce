.PHONY: all format lint test tests integration_tests help

# Default target executed when no arguments are given to make.
all: help

# Define variables for test paths
UNIT_TEST_PATH = tests/unit_tests/
INTEGRATION_TEST_PATH = tests/integration_tests/
TEST_FILE ?= tests/

######################
# TESTING
######################

# Run all tests (both unit and integration)
tests test:
	@echo "Running all tests..."
	uv run pytest \
		--verbose \
		--cov=langchain_salesforce \
		--cov-report=term-missing \
		$(TEST_FILE)

test_watch:
	uv run ptw \
		--snapshot-update \
		--now . \
		-- -vv $(TEST_FILE)

# Run integration tests only
integration_tests:
	@echo "Running integration tests..."
	uv run pytest \
		--verbose \
		--cov=langchain_salesforce \
		--cov-report=term-missing \
		$(INTEGRATION_TEST_PATH)

######################
# LINTING AND FORMATTING
######################

# Define a variable for Python files
PYTHON_FILES = .
MYPY_CACHE = .mypy_cache

# Lint all files
lint:
	uv run ruff check $(PYTHON_FILES)
	uv run ruff format $(PYTHON_FILES) --diff
	mkdir -p $(MYPY_CACHE) && uv run mypy $(PYTHON_FILES) --cache-dir $(MYPY_CACHE)

# Format all files
format:
	uv run ruff format $(PYTHON_FILES)
	uv run ruff check --select I --fix $(PYTHON_FILES)

# Lint only changed files (compared to master)
lint_diff:
	$(eval CHANGED_FILES := $(shell git diff --name-only --diff-filter=d master | grep -E '\.py$$' || echo ""))
	@if [ "$(CHANGED_FILES)" != "" ]; then \
		echo "Linting changed files: $(CHANGED_FILES)"; \
		uv run ruff check $(CHANGED_FILES); \
		uv run ruff format $(CHANGED_FILES) --diff; \
		mkdir -p $(MYPY_CACHE) && uv run mypy $(CHANGED_FILES) --cache-dir $(MYPY_CACHE); \
	else \
		echo "No Python files changed"; \
	fi

# Format only changed files (compared to master)
format_diff:
	$(eval CHANGED_FILES := $(shell git diff --name-only --diff-filter=d master | grep -E '\.py$$' || echo ""))
	@if [ "$(CHANGED_FILES)" != "" ]; then \
		echo "Formatting changed files: $(CHANGED_FILES)"; \
		uv run ruff format $(CHANGED_FILES); \
		uv run ruff check --select I --fix $(CHANGED_FILES); \
	else \
		echo "No Python files changed"; \
	fi

# Spell checking
spell_check:
	uv run codespell --toml pyproject.toml

spell_fix:
	uv run codespell --toml pyproject.toml -w

######################
# HELP
######################

help:
	@echo '===================='
	@echo 'Available targets:'
	@echo '===================='
	@echo 'Testing:'
	@echo '  test, tests          - run all tests with coverage'
	@echo '  integration_tests    - run integration tests only'
	@echo '  test_watch          - run tests in watch mode'
	@echo ''
	@echo 'Code Quality:'
	@echo '  lint                - run linters on all files'
	@echo '  format              - format all files'
	@echo '  lint_diff           - lint only changed files'
	@echo '  format_diff         - format only changed files'
	@echo '  spell_check         - check spelling'
	@echo '  spell_fix           - fix spelling errors'
	@echo ''
	@echo 'Usage:'
	@echo '  make test TEST_FILE=<path>  - run specific test file'
	@echo '===================='
