=======
History
=======

1.1.1 (Unreleased)
------------------
 * Remove foreign key from jobs to professional. (rudaporto)
 * Add logging with logstash to this package. (ericof)
 * Fix _update_job_on_knack. (rudaporto)
 * Change role to group in the Asset and Job workflows. (rudaporto)
 * Integrate workflow fix in briefy.common. (rudaporto)

1.1.0 (2016-10-04)
------------------

* BODY-53: Additional metadata from image (ericof).
* LEICA-50: Add custom resource event types for models: customer, comments, project. (rudaporto)
* Integrate new fixes on briefy.ws. (rudaporto)
* Deploy to update briefy.ws. (rudaporto)
* LEICA-56: New service to return delivery info for a job. (rudaporto)
* LEICA-58: Update Knack on job approval and rejection. (ericof)
* LEICA-47: Machine checking of assets. (ericof)
* Change to use gunicorn as wsgi service. (rudaporto)

1.0.0
-----

* LEICA-24: Clean up Job and Project models. (rudaporto)
* Add Metadata and Briefy Roles mixins to Job and Project. (rudaporto)
* LEICA-23: Add new Customer model and link to Project. (rudaporto)
* Update all postman tests and add into the project. (rudaporto)
* Recreate initial alembic migrations. (rudaporto)
* Update all tests and test data to fit the changes in the models. (rudaporto)
* LEICA-29: Add initial custom route factory for each model except JobLocation. (rudaporto)
* LEICA-38: Add uploaded_by to Asset (ericof).
* BODY-31: fixed briefy.ws issue. (rudaporto)
* LEICA-30: return comments list on the result payload of Jobs and Assets. (rudaporto)
* LEICA-31: Run asset.update_metada() method every time afeter asset model instance change. (rudaporto)
* LEICA-35: After Asset creation it will be automatic transitioned to pending state. (rudaporto)
* LEICA-28: Improve models to import data from knack. (jsbueno) (rudaporto)
* LEICA-36: Create events for Asset model instance lifecycle (POST, PUT, GET, DELETE) (rudaporto)
* BODY-45: Integrate briefy.ws fix. (rudaporto)
* BODY-40: Integrated briefy.common fix. (rudaporto)
* LEICA-42: Register sqlalchemy workflow context handlers for all models. (rudaporto)
* Speed up asset view tests by mocking calls to briefy-thumbor. (ericof)
* LEICA-37: Add versioning to Assets. (ericof)
* LEICA-44: After JOB creation automaticaly transition to in_qa state. (rudaporto)
* LEICA-45: Review asset workflow: rename rejected to edit and discarded to rejected. (rudaporto)
* LEICA-28: Adds knack_import script to fetch Knack JOB and Project data into the local database
* BODY-49: Integrate fix from briefy.ws. (rudaporto)
* LEICA-46: Update user_id data on all fields to user info map when object is serialized. (rudaporto)
* Integrate briefy.ws fixes for workflow endpoint POST with empty message attribute on body. (rudaporto)
* BODY-52: (hotfix) Quote filename for thumbor image signature. (ericof)

