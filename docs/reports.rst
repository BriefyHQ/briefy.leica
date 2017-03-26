Reports
--------

Customer Reports
++++++++++++++++



Financial Reports
+++++++++++++++++

Manual export
~~~~~~~~~~~~~

To generate the reports, access an updated installation of Leica -- meaning a recent database dump -- and 
run the following commands::

    cd briefy.leica
    source env/bin/activate
    source .env_dist
    python src/briefy/leica/tools/finance_csv_export.py

Two files will be exported to the `/tmp` folder::

    orders.csv
    assignments.csv


Automatic export
~~~~~~~~~~~~~~~~

Scheduled generation of finance reports is handled by `Ms. Ophelie`_ worker.

Ms. Ophelie will run, every 3 hours, a task to get the exports from Leica and save them
on Amazon S3.

The export generation is done in here, using the same routines from the manul export, but
are triggered by accesses to an internal endpoint /ms-ophelie/ not accessible through the
API Gateway.

Currently there are two endpoints:

  * /ms-ophelie/assignments: Generate the Assignments export
  * /ms-ophelie/orders: Generate the Orders export

The result is published on the Slack channel #finance-reports.


.. _`Ms. Ophelie`: https://github.com/BriefyHQ/ms.ophelie/
