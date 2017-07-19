.. highlight:: shell

Getting Started
===============

Prerequisites
-------------

* Git
* Python 3.6


Get the code
------------
Given you have privileges to access the codebase on GitHub, execute the following command on
a shell prompt::

  $ git clone git@github.com:BriefyHQ/briefy.leica.git

Local Install
-------------
Access the directory containing *briefy.leica* codebase::

  $ cd briefy.leica

Create a virtual environment::

  $ python3 -m venv .

Install package & dependencies
++++++++++++++++++++++++++++++

For development::


    $ ./bin/pip install -r requirements/dev.txt


For staging / production::

    $ ./bin/pip install -r requirements.txt


Running tests
-------------

To run all tests, first, it is needed to create all docker containers::

    $ make create_dockers

If containers are already created but not started::

    $ make start_dockers

Run all tests::

    $ make test


Check style::

    $ make lint

To run just a subset of the tests::

    $ ./bin/py.test tests/queue


Reporting Bugs
--------------

Report bugs at https://github.com/BriefyHQ/briefy.leica/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Generating the documentation
----------------------------

Install this package and its dependencies::

    $ ./bin/pip install -r requirements/dev.txt


Generate the HTML documentation::

    $ make docs_server

Open the your browser at http://localhost:8000
