SPHINXOPTS    = 
SPHINXAPIDOC  = sphinx-apidoc
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = docs/_build

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
SPHINXAPIDOC   = ./bin/sphinx-apidoc
SPHINXBUILD   = ./bin/sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you dont have Sphinx installed, grab it from http://sphinx-doc.org/)
endif
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) docs/
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 src/briefy/leica setup.py
	flake8 --ignore=D102,D103,D205,D101,D400,D210,D401,D100 tests

test: lint ## run tests quickly with the default Python
	ENV='test' py.test --no-print-logs --cov-report term-missing --cov=briefy.leica tests

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source briefy.leica py.test
	
		coverage report -m
		coverage html
		$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -rf $(BUILDDIR)/*
	rm -f docs/codebase/briefy*
	rm -f docs/codebase/modules.rst
	$(SPHINXAPIDOC) -M -d 1 -o docs/codebase src/briefy
	rm -f docs/codebase/modules.rst
	$(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml

docs_server: docs
	@cd $(BUILDDIR)/dirhtml; python3 -m http.server 8000

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

import_clean_db: clean_dockers create_dockers import_knack
	echo "Start the a clean import.."

import_knack:
	IMPORT_KNACK=True python src/briefy/leica/tools/import_all.py
	unset IMPORT_KNACK

dumpdb_prod:
	pg_dump -Fc -h briefy-services.cbpyycv8xvtn.eu-central-1.rds.amazonaws.com \
	-p 5432 -U leica_usr --exclude-schema=tiger --exclude-schema=topology \
	-d leica > /tmp/production-leica.dump
	sudo chmod 0644 /tmp/production-leica.dump

dumpdb_stg:
	pg_dump -Fc -h briefy-services.c2q3x2i4qnm7.us-east-1.rds.amazonaws.com \
	-p 5432 -U leica_usr --exclude-schema=tiger --exclude-schema=topology \
	-d leica > /tmp/staging-leica.dump
	sudo chmod 0644 /tmp/staging-leica.dump

uploaddb_live_to_stg:
	scp live:/tmp/production-leica.dump /tmp/production-leica.dump
	scp /tmp/production-leica.dump stg:/tmp/production-leica.dump

	
restoredb_prod_local: clean_dockers create_dockers
	scp live:/tmp/production-leica.dump /tmp/production-leica.dump
	pg_restore --no-owner -x -h localhost -p 9999 -U briefy -W -d briefy-leica /tmp/production-leica.dump

restoredb_stg_local: clean_dockers create_dockers
	scp stg:/tmp/staging-leica.dump /tmp/staging-leica.dump
	pg_restore --no-owner -x -h localhost -p 9999 -U briefy -W -d briefy-leica /tmp/staging-leica.dump

start_dockers:
	docker start redis
	docker start memcached
	docker start sqs
	docker start briefy-leica-test
	docker start briefy-leica-unit_test

stop_dockers: ## stop and remove docker containers
	docker stop redis
	docker stop memcached
	docker stop sqs
	docker stop briefy-leica-test
	docker stop briefy-leica-unit_test

clean_dockers: stop_dockers
	docker rm redis
	docker rm memcached
	docker rm sqs
	docker rm briefy-leica-test
	docker rm briefy-leica-unit_test

export_db_env:
	export DATABASE_URL=postgresql://briefy:briefy@127.0.0.1:9979/briefy-leica
	export DATABASE_TEST_URL=postgresql://briefy:briefy@127.0.0.1:9978/briefy-leica-unit_test

create_dockers: export_db_env
	docker run -d -p 127.0.0.1:6379:6379 --name redis redis
	docker run -p 127.0.0.1:11211:11211 --name memcached -d memcached memcached -m 128
	docker run -d -p 127.0.0.1:5000:5000 --name sqs briefy/aws-test:latest sqs
	export SQS_IP=127.0.0.1 SQS_PORT=5000
	docker run -d -p 127.0.0.1:9979:5432 -e POSTGRES_PASSWORD=briefy -e POSTGRES_USER=briefy -e POSTGRES_DB=briefy-leica --name briefy-leica-test mdillon/postgis:9.6
	docker run -d -p 127.0.0.1:9978:5432 -e POSTGRES_PASSWORD=briefy -e POSTGRES_USER=briefy -e POSTGRES_DB=briefy-leica-unit_test --name briefy-leica-unit_test mdillon/postgis:9.6
	echo "Waiting Posgtres to start"
	sleep 40s
