Sync
----

Rules to sync information between Knack and Leica.

Knack (Job)
+++++++++++

A Job on knack has two fields to hold workflow: `Approval Status` and `Client Job Status`.

* `Approval Status`

  * Awaiting for Submission
  * Awaiting Approval
  * Approved
  * Not Approved
  * Updated And Waiting for Approval (after rework)


* `Client Job Status`

  * In Scheduling Process
  * Scheduled
  * In QA Process
  * Completed
  * In Revision
  * Cancelled


Events
""""""

* Job created on Knack: post Leica, update briefy_id on knack
* Professional add submission link: (change state to Awaiting Approval)

  * Import Job if not imported in state in_qa: post Leica, update briefy_id on knack
  * Import Assets in state pending: download gdrive, upload s3, post to add asset Leica
  * Or update Job information on Leica: transition to In QA (open question: back to Knack `Client Job Status`)

* QA approve Job: (`Client Job Status` -> Completed  and `Approval Status` -> Approved)

  * Update Job on Leica
  * Update Assets on Leica (how to do it? using client delivery link and compare image names? moving to reserved state with special comment?)

* QA reject Job:

  * Update Job on Leica
  * Update Assets on Leica (how to do it?)


* Open questions

  * How to deal with assets from jobs approved outside Leica?


Knack (Project)
+++++++++++++++

Knack (Customer)
++++++++++++++++
