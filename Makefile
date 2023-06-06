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
	# note: don't change the order of the commands heres

	set -ex

	# test default group option
	kxgr build --verbose

	# group 1
	kxgr --help
	kxgr --version
	kxgr build --verbose --group group1 --all
	kxgr build --verbose --group group1
	kxgr build --verbose --group group1 --services service1-1
	kxgr pull --verbose --group group1 --all
	kxgr pull --verbose --group group1
	kxgr pull --verbose --group group1 --services service1-1
	kxgr ext start --verbose --group group1 --all --options -d
	kxgr ext restart --verbose --group group1 --all --options -d
	kxgr exec --verbose --group group1 --service service1-1 --options -T --cmd env
	kxgr stop --verbose --group group1 --all
	kxgr run --verbose --group group1 --service service1-1 --options -T --cmd env
	kxgr down --verbose --group group1

	# group 2
	kxgr build --verbose --group group2 --all
	kxgr build --verbose --group group2
	kxgr build --verbose --group group2 --services service2-1
	kxgr pull --verbose --group group2 --all
	kxgr pull --verbose --group group2
	kxgr pull --verbose --group group2 --services service2-1
	kxgr ext start --verbose --group group2 --all --options -d
	kxgr ext restart --verbose --group group2 --all --options -d
	kxgr exec --verbose --group group2 --service service2-1 --options -T --cmd env
	kxgr stop --verbose --group group2 --all
	kxgr run --verbose --group group2 --service service2-1 --options -T --cmd env
	kxgr down --verbose --group group2

	# group mix
	kxgr build --verbose --group group-mix --all
	kxgr build --verbose --group group-mix
	kxgr build --verbose --group group-mix --services service1-1,service2-1
	kxgr pull --verbose --group group-mix --all
	kxgr pull --verbose --group group-mix
	kxgr pull --verbose --group group-mix --services service1-1,service2-1
	kxgr ext start --verbose --group group-mix --all --options -d
	kxgr ext restart --verbose --group group-mix --all --options -d
	kxgr exec --verbose --group group-mix --service service2-1 --options -T --cmd env
	kxgr stop --verbose --group group-mix --all
	kxgr run --verbose --group group-mix --service service2-1 --options -T --cmd env
	kxgr down --verbose --group group-mix

	# general tests main profile/plugins
	kxgr build --verbose --group group1
	kxgr config --verbose --group group1
	kxgr create --verbose --group group1
	kxgr ext start --verbose --group group1 --options -d
	kxgr ext restart --verbose --group group1 --options -d
	kxgr exec --verbose --group group1 --service service1-1 --options -T --cmd env
	kxgr images --verbose --group group1
	kxgr logs --verbose --group group1
	kxgr port --verbose --group group1
	kxgr ps --verbose --group group1
	kxgr pull --verbose --group group1
	kxgr push --verbose --group group1
	kxgr run --verbose --group group1 --service service1-1 --options -T --cmd env
	kxgr top --verbose --group group1
	kxgr up --verbose --group group1 --options -d
	kxgr version --verbose --group group1
	kxgr events --verbose --group group1 --options --json --dry-run
	# keep these ones at the end
	kxgr pause --verbose --group group1
	kxgr unpause --verbose --group group1
	kxgr kill --verbose --group group1
	kxgr stop --verbose --group group1
	kxgr rm --verbose --group group1 --options --force
	kxgr down --verbose --group group1
