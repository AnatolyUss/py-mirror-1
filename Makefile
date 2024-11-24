PYTHON_GLOBAL = python
VENV_DIR = py_mirror_1_venv
PIP = $(VENV_DIR)/bin/pip
PYTHON = $(VENV_DIR)/bin/python
MYPY = $(VENV_DIR)/bin/mypy
LINTER = $(VENV_DIR)/bin/ruff
TESTS = py_mirror/tests
DOCKER = docker

venv:
	$(PYTHON_GLOBAL) -m venv $(VENV_DIR)

install:
	$(PIP) install -r requirements.txt
	rm requirements.txt
	$(PIP) freeze >> requirements.txt

test:
	$(VENV_DIR)/bin/pytest $(TESTS)

lint:
	$(LINTER) check

format:
	$(LINTER) format
	git status

type-check:
	$(MYPY) -p py_mirror

lf:
	make lint
	make format

ftc:
	make format
	make type-check
lftc:
	make lint
	make format
	make type-check

lftct:
	make lint
	make format
	make type-check
	make test

run-api:
	$(PYTHON) main.py --run-api

init-db:
	$(PYTHON) main.py --init-db

clean:
	rm -rf $(VENV_DIR)
	rm -rf *.egg-info
	rm -rf __pycache__

compose-up:
	$(DOCKER) compose -f docker-compose.yml -p py-mirror-1 up -d

help:
	@echo "Makefile for Python project"
	@echo "Targets:"
	@echo "  venv        Create VENV"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linter"
	@echo "  format      Format code"
	@echo "  type-check  Perform static type checking"
	@echo "  ftc         Format code, perform static type checking"
	@echo "  lftc        Lint-format code, perform static type checking"
	@echo "  lftct       Lint-format code, perform static type checking, run tests"
	@echo "  lf          Lint and format code"
	@echo "  run-api     Run the API"
	@echo "  init-db     Run initial DB migration"
	@echo "  clean       Remove the virtual environment and other generated files"
	@echo "  compose-up  Run docker compose up"
