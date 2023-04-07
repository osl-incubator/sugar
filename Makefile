.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

ARGS:=

.PHONY:help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY:clean
clean: ## remove build artifacts, compiled files, and cache
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name
	find . -name '__pycache__' -exec rm -fr '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +{} +
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

.PHONY:lint
lint:
	pre-commit run --all-files


.PHONY:test
test: ## run tests quickly with the default Python
	pytest -s -vv tests ${ARGS}


.PHONY:docs-build
docs-build:
	mkdocs build --config-file docs/mkdocs.yaml

.PHONY: docs-preview
docs-preview: docs-build
	mkdocs serve --watch docs --config-file docs/mkdocs.yaml

.PHONY:build
build:
	poetry build


.ONESHELL:
.PHONY: smoke-tests
smoke-tests:
	set -ex
	# group 1
	containers-sugar --help
	containers-sugar --version
	containers-sugar build --verbose --group group1 --all
	containers-sugar build --verbose --group group1
	containers-sugar build --verbose --group group1 --services service1-1
	containers-sugar pull --verbose --group group1 --all
	containers-sugar pull --verbose --group group1
	containers-sugar pull --verbose --group group1 --services service1-1
	containers-sugar start --verbose --group group1 --all --options -d
	containers-sugar restart --verbose --group group1 --all --options -d
	containers-sugar exec --verbose --group group1 --service service1-1 --options -T --cmd env
	containers-sugar stop --verbose --group group1 --all
	containers-sugar run --verbose --group group1 --service service1-1 --options -T --cmd env
	containers-sugar down --verbose --group group1
	# group 2
	containers-sugar build --verbose --group group2 --all
	containers-sugar build --verbose --group group2
	containers-sugar build --verbose --group group2 --services service2-1
	containers-sugar pull --verbose --group group2 --all
	containers-sugar pull --verbose --group group2
	containers-sugar pull --verbose --group group2 --services service2-1
	containers-sugar start --verbose --group group2 --all --options -d
	containers-sugar restart --verbose --group group2 --all --options -d
	containers-sugar exec --verbose --group group2 --service service2-1 --options -T --cmd env
	containers-sugar stop --verbose --group group2 --all
	containers-sugar run --verbose --group group2 --service service2-1 --options -T --cmd env
	containers-sugar down --verbose --group group2
	# group mix
	containers-sugar build --verbose --group group-mix --all
	containers-sugar build --verbose --group group-mix
	containers-sugar build --verbose --group group-mix --services service1-1,service2-1
	containers-sugar pull --verbose --group group-mix --all
	containers-sugar pull --verbose --group group-mix
	containers-sugar pull --verbose --group group-mix --services service1-1,service2-1
	containers-sugar start --verbose --group group-mix --all --options -d
	containers-sugar restart --verbose --group group-mix --all --options -d
	containers-sugar exec --verbose --group group-mix --service service2-1 --options -T --cmd env
	containers-sugar stop --verbose --group group-mix --all
	containers-sugar run --verbose --group group-mix --service service2-1 --options -T --cmd env
	containers-sugar down --verbose --group group-mix
