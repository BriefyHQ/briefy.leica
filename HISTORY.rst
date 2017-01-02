=======
History
=======

1.1.1 (Unreleased)
------------------
     * Remove foreign key from jobs to professional. (rudaporto)
     * Add logging with logstash to this package. (ericof)
     * LEICA-60: Move image file on Asset creation or update. (ericof)
     * Fix _update_job_on_knack. (rudaporto)
     * Change role to group in the Asset and Job workflows. (rudaporto)
     * Integrate workflow fix in briefy.common. (rudaporto)
     * BODY-62: Implement pagination. (ericof)
     * LEICA-63: Improve workflows. (ericof)
     * LEICA-09: Improve Customers, Projects and Jobs import. Add service to run the import by API call. (rudaporto)
     * LEICA-69: Create new endpoints to sync with knack individual records. (rudaporto)
     * LEICA-70: New endpoint to log requests from knack. (rudaporto)
     * Moved import/sync endpoints path to reside inside /knack namespace. (rudaporto)
     * LEICA-74: Backport image validation code from Ms. Laure. (ericof)
     * Integrate HEAD method improvements of briefy.ws. (rudaporto)
     * Use last version of Briefy.ws. (aivuk)
     * Configure job service to allow filter and sort usign Project.title. (aivuk)
     * LEICA-73: Document Leica data models and improve fields/relationships (ericof)
     * LEICA-61: Merge from AGFA. (ericof)
     * LEICA-95: Update Professional model (merge from AGFA). (ericof)
     * LEICA-71: Add "Extra Compensation" Field to Jobs. (ericof)
     * LEICA-92: Update Job model. (ericof)
     * LEICA-93: Update Customer model. (ericof)
     * LEICA-94: Update Project model. (ericof)
     * Update models, migration and tests (rudaporto).
     * Sync JobOrder (Location, Assignment, Comment) and Photographer(working locations) (rudaporto).
     * New sync code to update brief_id in all profiles objects in knack (rudaporto).
     * New mixin for LeicaRoles and mixins for local roles of Customer, Project, Order and Assignment (rudaporto).
     * Improve sync classes to get roles from the knack obj, convert to rolleiflex id and add as local role (rudaporto).
     * Some minor improvents to import more phone numbers from Photographers (rudaporto).
     * BODY-91: Remove all load strategy with lazy="joined" (rudaporto).
     * Fix Project __actors__, listing, and summary fields (rudaporto).
     * Improve sync to parse phone numbers for the JobOrder contact (rudaporto).
     * Create new column_property attributes using subquery to easy filter JobAssignment by some JobOrder attributes (rudaporto).
     * Fix: upgrade s3transfer from 1.1.2 to 0.1.10 to fix conflict version with boto libs (rudaporto).
     * Update all Leica local roles to use new relationship and association_proxy attributes (rudaporto).
     * Update sync to the new association_proxy attributes (rudaporto).
     * Update JobAssignment sync to create local role also for the professional (rudaporto)
     * LEICA-120: include additional fields from JobOrder to JobAssignment and expose then in /jobs search (rudaporto).
     * Update Professional and JobLocation summary fields (rudaporto).
     * Small fixes in the sync classes (rudaporto).
     * Change default LeicaRolesMixin association_proxy to return only a single element: this enable filter by the user ID. (rudaporto)
     * Add all local role association_proxy fields as filter_related_fields to be searchable on the views using the user ID. (rudaporto)
     * Improve Customer model with new relationships that return business and billing addres as a attribute and expose then in the payload (rudaporto).
     * Improve CustomerContact model defining summary and listing attributes (rudaporto).
     * Remove transaction manager and control commit manually in the import / sync classes and remove (rudaporto).
     * Change migration to new address format from briefy.common (rudaporto).
     * Update summary attributes for job location, professional and professional location (rudaporto).
     * Update additional fielter fields for jobs, order, professional and projects views (rudaporto).
     * Change field locations to location on JobOrder since for now we just have one location (rudaporto).
     * New attribute (relationship uselist=False) on professional model: main_location (rudaporto).
     * Customized to_dict and to_liting_dict on professional model (rudaporto).
     * Change number_of_assets Order field to number_required_assets (rudaporto).
     * Update import to generate the Order slug from the knack.job_id (internal) (rdaporto).
     * Remove the last lazy='joined' to improve listing latency (rudaporto).
     * Added new field set_type to show and filter different types of sets in QA (rudaporto).
     * Refactory _summarize_relationships and also insert it in the default to_dict and to_listing_dict (rudaporto).
     * Update import Job to populate set_type and also added set_type to the JobAssignment listing (rudaporto).
     * Fix slug generation when import form knack (rudaporto).
     * Added new field slug in the JobAssingmnet and update db migration and import from knack (rudaporto).
     * New function that use the insert context to create JobAssigmnet slug from the JobOrder slug (rudaporto).
     * Added database models: JobPool and ProfessionalsInPool (association model between JobPool and Professional) (rudaporto).
     * Basic workflow for a JobPool model (rudaporto).
     * Added new ForeignKey pool_id (nullable=True) in JobAssignment model to link an JobAssignment to a JobPool (rudaporto).
     * Added resource view /pools to manage JobPools (rudaporto).
     * Update database fixtures to support composed primary keys (rudaporto).


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

1.0.0 (2016-09-27)
------------------
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

