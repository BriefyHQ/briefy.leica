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
	flake8 src/briefy/leica setup.py migrations
	flake8 --ignore=D102,D103,D205,D101,D400,D210,D401,D100 tests

test: lint ## run tests quickly with the default Python
	py.test --cov-report term-missing --cov=briefy.leica tests

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

import_clean_db: clean_dockers create_dockers
	echo "Waiting Posgtres to start"
	sleep 10
	alembic upgrade head
	python src/briefy/leica/tools/customer_import.py
	python src/briefy/leica/tools/project_import.py
	python src/briefy/leica/tools/photographer_import.py
	python src/briefy/leica/tools/job_import.py

start_dockers:
	docker start sqs
	docker start briefy-leica-test
	docker start briefy-leica-unit_test

stop_dockers: ## stop and remove docker containers
	# sqs
	docker stop sqs
	docker stop briefy-leica-test
	docker stop briefy-leica-unit_test

clean_dockers: stop_dockers
	docker rm sqs
	docker rm briefy-leica-test
	docker rm briefy-leica-unit_test

export_db_env:
	export DATABASE_URL=postgresql://briefy:briefy@127.0.0.1:9999/briefy-leica
	export DATABASE_TEST_URL=postgresql://briefy:briefy@127.0.0.1:9998/briefy-leica-unit_test

create_dockers: export_db_env
	docker run -d -p 127.0.0.1:5000:5000 --name sqs briefy/aws-test:latest sqs
	export SQS_IP=127.0.0.1 SQS_PORT=5000
	docker run -d -p 127.0.0.1:9999:5432 -e POSTGRES_PASSWORD=briefy -e POSTGRES_USER=briefy -e POSTGRES_DB=briefy-leica --name briefy-leica-test mdillon/postgis:9.5
	docker run -d -p 127.0.0.1:9998:5432 -e POSTGRES_PASSWORD=briefy -e POSTGRES_USER=briefy -e POSTGRES_DB=briefy-leica-unit_test --name briefy-leica-unit_test mdillon/postgis:9.5

