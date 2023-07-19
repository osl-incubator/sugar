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


# SMOKE TESTS

.ONESHELL:
.PHONY: docker-killall
docker-killall:
	set -ex
	docker kill `docker ps -q` || true
	set +ex

.ONESHELL:
.PHONY: smoke-test-group-1
smoke-test-group-1: docker-killall
	set -ex
	# group 1
	sugar build --verbose
	sugar build --verbose --group group1 --all
	sugar build --verbose --group group1
	sugar build --verbose --group group1 --services service1-1
	sugar pull --verbose --group group1 --all
	sugar pull --verbose --group group1
	sugar pull --verbose --group group1 --services service1-1
	sugar ext start --verbose --group group1 --all --options -d
	sugar ext restart --verbose --group group1 --all --options -d
	sugar exec --verbose --group group1 --service service1-1 --options -T --cmd env
	sugar stop --verbose --group group1 --all
	sugar run --verbose --group group1 --service service1-1 --options -T --cmd env
	sugar down --verbose --group group1
	set +ex

.ONESHELL:
.PHONY: smoke-test-group-2
smoke-test-group-2: docker-killall
	set -ex
	# group 2
	sugar build --verbose --group group2 --all
	sugar build --verbose --group group2
	sugar build --verbose --group group2 --services service2-1
	sugar pull --verbose --group group2 --all
	sugar pull --verbose --group group2
	sugar pull --verbose --group group2 --services service2-1
	sugar ext start --verbose --group group2 --all --options -d
	sugar ext restart --verbose --group group2 --all --options -d
	sugar exec --verbose --group group2 --service service2-1 --options -T --cmd env
	sugar stop --verbose --group group2 --all
	sugar run --verbose --group group2 --service service2-1 --options -T --cmd env
	sugar down --verbose --group group2
	set +ex

.ONESHELL:
.PHONY: smoke-test-group-mix
smoke-test-group-mix: docker-killall
	set -ex
	# group mix
	sugar build --verbose --group group-mix --all
	sugar build --verbose --group group-mix
	sugar build --verbose --group group-mix --services service1-1,service2-1
	sugar pull --verbose --group group-mix --all
	sugar pull --verbose --group group-mix
	sugar pull --verbose --group group-mix --services service1-1,service2-1
	sugar ext start --verbose --group group-mix --all --options -d
	sugar ext restart --verbose --group group-mix --all --options -d
	sugar exec --verbose --group group-mix --service service2-1 --options -T --cmd env
	sugar stop --verbose --group group-mix --all
	sugar run --verbose --group group-mix --service service2-1 --options -T --cmd env
	sugar down --verbose --group group-mix
	set +ex

.ONESHELL:
.PHONY: smoke-test-main
smoke-test-main: docker-killall
	set -ex
	# general tests main profile/plugins
	sugar build --verbose --group group1
	sugar config --verbose --group group1
	sugar create --verbose --group group1
	sugar ext start --verbose --group group1 --options -d
	sugar ext restart --verbose --group group1 --options -d
	sugar exec --verbose --group group1 --service service1-1 --options -T --cmd env
	sugar images --verbose --group group1
	sugar logs --verbose --group group1
	# port is not complete supported
	# sugar port --verbose --group group1 --service service1-1
	sugar ps --verbose --group group1
	sugar pull --verbose --group group1
	sugar push --verbose --group group1
	sugar run --verbose --group group1 --service service1-1 --options -T --cmd env
	sugar top --verbose --group group1
	sugar up --verbose --group group1 --options -d
	sugar version --verbose
	# port is not complete supported
	# sugar events --verbose --group group1 --service service1-1 --options --json --dry-run
	set +ex


.ONESHELL:
.PHONY: smoke-test-defaults
smoke-test-defaults: docker-killall
	$(MAKE) docker-killall
	set -ex
	export KXGR_PROJECT_NAME="test-`python -c 'from uuid import uuid4; print(uuid4().hex[:7])'`"
	echo $$KXGR_PROJECT_NAME
	sugar build --verbose --group group-defaults
	sugar ext start --verbose --group group-defaults --options -d
	sugar ext restart --verbose --group group-defaults --options -d
	docker ps|grep $$KXGR_PROJECT_NAME
	sugar ext stop --verbose --group group-defaults
	set +ex

.ONESHELL:
.PHONY: smoke-final-tests
smoke-final-tests: docker-killall
	# keep these ones at the end
	sugar ext restart --verbose --group group-defaults --options -d
	sugar pause --verbose --group group1
	sugar unpause --verbose --group group1
	sugar kill --verbose --group group1
	sugar stop --verbose --group group1
	sugar rm --verbose --group group1 --options --force
	sugar down --verbose --group group1

.ONESHELL:
.PHONY: smoke-tests
smoke-tests: smoke-test-group-1 smoke-test-group-2 smoke-test-group-mix smoke-test-main smoke-test-defaults smoke-final-tests
	sugar --help
	sugar --version
