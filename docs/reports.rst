Reports
--------

Customer Reports
++++++++++++++++

Only one report is available for customers:

  * /reports/customer/projects/{id}: Generate Order report about the project with the given id.


Financial Reports
+++++++++++++++++

Automatic export
~~~~~~~~~~~~~~~~

Scheduled generation of finance reports is handled by `Ms. Ophelie`_ worker.

Ms. Ophelie will run, periodically, a task to get the exports from Leica and save them
on Amazon S3.

The export generation is done in here, using the same routines from the manul export, but
are triggered by accesses to an internal endpoint /ms-ophelie/ not accessible through the
API Gateway.

Currently there are the following endpoints:

  * /ms-ophelie/assignments/all: Generate the Assignments export for all projects.
  * /ms-ophelie/assignments/active: Generate the Assignments export for active projects.
  * /ms-ophelie/orders/all: Generate the Orders export for all projects.
  * /ms-ophelie/orders/active: Generate the Orders export for active projects.
  * /ms-ophelie/customers/all: Generate the Customers export.
  * /ms-ophelie/professionals/all: Generate the Professionals export.

The result is published on the Slack channel #finance-reports.


.. _`Ms. Ophelie`: https://github.com/BriefyHQ/ms.ophelie/
