Briefy Leica
============

Leica is the internal sysem to handle images and other assets
from upload by the professionals up to delivering, including internal
QA steps and so on.

A comprehensive documentation is available at the `Developer Documentation`_ server.


TODO
====

* Add unit tests for all versions and history endpoints
* Update workflow for required fields.
* Implement customer roles and project roles in the CustomerUserProfile
* Implement unit tests to check local roles inheritance (traverse)
* Implement unit tests for local permissions
* Fix many to many relationship between professional and pool with sqlalchemy_continuum

Code Health
===========
This service codebase is tested using Travis CI

============ ======================================================================================================================== 
Branch       Status
============ ========================================================================================================================
`master`_     .. image:: https://travis-ci.com/BriefyHQ/briefy.leica.svg?token=APuRM8itTuPw15pKpJWp&branch=master
                 :target: https://travis-ci.com/BriefyHQ/briefy.leica

`develop`_    .. image:: https://travis-ci.com/BriefyHQ/briefy.leica.svg?token=APuRM8itTuPw15pKpJWp&branch=develop
                 :target: https://travis-ci.com/BriefyHQ/briefy.leica
============ ========================================================================================================================



.. _`master`: https://github.com/BriefyHQ/briefy.leica/tree/master
.. _`develop`: https://github.com/BriefyHQ/briefy.leica/tree/develop
.. _`Developer Documentation`: https://docs.stg.briefy.co/briefy.leica/
