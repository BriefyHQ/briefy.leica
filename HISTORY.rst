=======
History
=======

2.0.27 (2017-03-10)
-------------------

    * Implemented script to fix assginments with shoot time in the past and stucked in the assigned state (rudaporto).
    * Update documentation with database backup and restore and how to execute agoda delivery sftp procedure (rudaporto).


2.0.26 (2017-03-08)
-------------------

    * Finance export: Added submission date (first) column to Assignment export (rudaporto).
    * Finance export: change file format of Order and Assignment to use tab delimiter (rudaporto).
    * Added oneshot script to update gdrive delivery links for Agoda orders using slack history file (rudaporto).


2.0.25 (2017-03-06)
-------------------

    * Change the default Project.availability_window to 6 days (rudaporto).
    * Update finance report to have the option to export Order customer comments (rudaporto).
    * When remove availability dates, keep copy the payout from the old assignment to the new (rudaporto).
    * Fix: Order transition set_availability from assigned to assigned was wrong defined (rudaporto).
    * Update availability dates validation to be change the availability window to zero when the user is PM (rudaporto).


2.0.24 (2017-03-01)
-------------------

    * Validate availability dates using Project.availability_window (days) value (rudaporto).

2.0.23 (2017-02-28)
-------------------

    * Fix: when new assignment is created also copy project_managers local role from the order (rudaporto).
    * Fix: when new assignment is created make sure set type will be 'new' (rudaporto).

2.0.22 (2017-02-28)
-------------------

    * New task to move orders from delivery do completed (rudaporto).
    * Review Order accept workflow transition and guard (rudaporto).
    * Change Order cancel workflow transition to using the cancellation window from Project (rudaporto).
    * Update default values for new Project: cancellation_window=1, availability_window=7, approval_window=5 (rudaporto).
    * Update Project.approval_windows docs: value should be business days (rudaporto).
    * New script (finance_csv_export.py) in tools to export all orders and assignments to the invoice system (rudaporto).


2.0.21 (2017-02-27)
-------------------

    * Fix: fields map overwrite cause Assignment.professional_user not being set. (rudaporto).
    * Added new config SCHEDULE_DAYS_LIMIT to easy change the number of days before schedule (rudaporto).

2.0.20 (2017-02-25)
-------------------

    * Added Assignment.delivery as a listing attribute (rudaporto).


2.0.19 (2017-02-24)
-------------------

    * New release to update briefy.common (rudaporto).


2.0.18 (2017-02-24)
-------------------

    * Added Order.customer_order_id to summary attributes, ms.laure needs on the payload of Assignment (rudaporto).

2.0.17 (2017-02-24)
-------------------

    * Created new script to setup demo data for Booking.com visit (rudaporto).
    * Make ProfileUser email unique field (rudaporto).
    * Added new validator to check if UserProfile or CustomerUserProfile email already in use (rudaporto).
    * Added delivery and delivery_date to the Order summary attributes (rudaporto).


2.0.16 (2017-02-22)
-------------------

    * Scouters can approve a new Creative (ericof).

2.0.15 (2017-02-22)
-------------------

    * Fix Order.location edit: added order_id to OrderLocation summary fields (rudaporto).

2.0.14 (2017-02-22)
-------------------

    * Machine validation: Create comment only when the set is invalidated (ericof).
    * Machine validation: Transition/Comment on invalidation should use complete feedback (ericof).
    * Remove Assignment._timezone_observer. Order will take care of update assignment.timezone (rudaporto).
    * Fix circular serialization: Order.location will be serialized as summary in the Order and Assignment (rudaporto).
    * Improve Assignment serialization: Assignment.order will ber serialized as summary (rudaporto).
    * Fix OrderLocation edit. Fixed by Removing Assignment._timezone_observer and fix Order.location circular serialization (rudaporto).
    * Set Scout Manager on Order and Assignment (ericof).
    * Add assign_pool transition to the list of transitions to be considered when updating the assignment_date (ericof).

2.0.13 (2017-02-21)
-------------------

    * Improve Assignment.location relationshi: simplify secondary parameter (rudaporto).
    * Excludes from colander schema generation OrderLocation.assignments attribute (rudaporto).
    * Excludes from to_dict serialisation Assignment.active_order attribute (rudaporto).
    * Update .gitignore to avoid deploy failures (rudaporto).
    * Added pool (summary) attribute to the Assignment listing (rudaporto).

2.0.12 (2017-02-21)
-------------------

    * Fix: Avoid try to do the delivery transition if Order already delivered (rudaporto).

2.0.11 (2017-02-21)
-------------------

    * Fix: Order tech requirement was reporting incorrect values from project (ericof).
    * Fix transaction and database configuration on tasks worker (rudaporto).

2.0.10 (2017-02-20)
-------------------

    * Added new log module to handle special loggers creation and adjust worker and tasks to use new loggers (rudaporto).

2.0.9 (2017-02-20)
------------------
    * Create leica_tasks main script and two tasks: publish to pool and move to awainting assets (rudaporto).


2.0.8 (2017-02-20)
------------------

    * Order: Add timezone attribute (ericof).
    * Order: Add scheduled_datetime, deliver_date, last_deliver_date, accept_date (ericof).
    * Order: Add script to update computed dates (ericof).
    * Add project pool_id attribute (ericof).
    * Add project delivery info attribute (ericof).
    * Script to move assignments from scheduled to awaiting assets (rudaporto).
    * Script to move assignments to the Pool (rudaporto).
    * Update worker approve_assignment action to execute the Order workflow delivery transition (rudaporto)
    * Add Orders by Project report to customers (ericof).
    * Return scheduled_datetime in order listings (ericof).

2.0.7 (2017-02-17)
------------------

    * Script to update all Agoda orders with original latitude and longitude from Agoda spreadsheets (rudaporto).


2.0.6 (2017-02-16)
------------------

    * Fix Order.to_dict to avoid failure when there is no active Assignment (rudaporto).
    * Leica Worker: Support handling ignored assignments (ericof).
    * Improve new assignment creation function to also receive the old assignment (rudaporto).
    * Change unassign and reshoot transition create a new assignment before cancel or complete the old one (rudaporto).
    * Cancel an Assignment will always set payout_value to zero (rudaporto).
    * Change newrelic config to ignore pyramid.httpexceptions:HTTPForbidden exceptions (rudaporto).
    * Change can_cancel logic for Order and Assignment (rudaporto).
    * Remove Assignment.scheduled_datetime when it's cancelled (rudaporto).


2.0.5 (2017-02-15)
------------------

    * Update and merge all Leica fixes in the worker (rudaporto).
    * Fix Leica worker (jsbueno).

2.0.4 (2017-02-15)
------------------

    * Split workflows for Briefy and Customer profiles (ericof).
    * Fix Submission Date calculation on Assignment (ericof).
    * Expose initial password on UserProfile creation (ericof).
    * Set timezone on new and updated OrderLocations (ericof).
    * Improve Order to_dict to add actors info to the current Assignment (rudaporto).
    * Improve LeicaBriefyRoles._apply_actors_info to also accept another instance object and not use self (rudaporto).
    * Improve Professional and Assignment summary attributes (rudaporto).
    * Fix remove_availability transition: now the new assignment is created after cancel the old one (rudaporto).
    * Change Assignment assign transition to require payout currency, value and travel expenses (rudaporto).
    * Change remove availability to create the assignment inside the transition (rudaporto).
    * Scout dashboard now support links on projects (ericof).
    * Added payout value and currency and travel expenses to the summary attributes (rudaporto).
    * Create new assignment function can now copy the payout value, currency and travel expenses (rudaporto).
    * Update reshoot to receive all payout value, currency and travel expenses and use it to assign the new assignment (rudaporto).
    * Update new shoot to use the new option to copy payout values from the old shoot (rudaporto).


2.0.3 (2017-02-14)
------------------

    * Fix add creative with portfolio link (rudaporto).
    * Split workflows for Briefy and Customer profiles (ericof).

2.0.2 (2017-02-14)
------------------

    * Fix primary key of dashboard declarative models (rudaporto).

2.0.1 (2017-02-14)
------------------

    * Added timezone attribute to Assignment summary and fix the timezone property (rudaporto).
 

2.0.0 (2017-02-13)
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
     * Added database models: Pool and ProfessionalsInPool (association model between Pool and Professional) (rudaporto).
     * Basic workflow for a Pool model (rudaporto).
     * Added new ForeignKey pool_id (nullable=True) in JobAssignment model to link an JobAssignment to a Pool (rudaporto).
     * Added resource view /pools to manage JobPools (rudaporto).
     * Update database fixtures to support composed primary keys (rudaporto).
     * Add Pool sync/import script and classes (rudaporto).
     * Fix Pool and Professional association relationships and update tests (rudaporto).
     * Update initial database migration script with all model changes (rudaporto).
     * LEICA-128: Refactor Job classes names following the changes as Assignment or Order (rudaporto).
     * LEICA-132: Add new fields to Pool and fix Professionls in Pool import. Add pool attribute to Assignment list and filter (rudaporto).
     * LEICA-133: Added Scouting Dashboard endpoints (rudaporto).
     * LEICA-134: Added QA Dashboard endpoints (rudaporto).
     * LEICA-135: Added Professional and Customer Dashboard endpoints (rudaporto).
     * Add new field for Professional: accept_travel (boolean) (rudaporto).
     * Remove all binary=false from UUID fields (rudaporto).
     * Adjust users sync to update Knack Profile.briefy_id if not equal to same user.briefy_id in Rolleiflex (rudaporto).
     * New descriptor to help set and get from unary relationships like Order.location (rudaporto).
     * Review __raw_acl__ attribute on all models (rudaporto).
     * Improve import to set permissions for each local role imported (rudaporto).
     * New base class to test dashboard views and test cases for all implemented dashboards: QA, Scout, Professional, Customer (rudaporto).
     * Change customer and professional dashboard queries and implement default_filter (view) to add parameters to the query (rudaporto).
     * Update Comments model to accept author_role, to_role and internal attributes (rudaporto).
     * Create new model UserProfile and change Professional model to use it as base class (rudaporto).
     * Refactor classes that uses ContactInfoMixin to use version from briefy.common (rudaporto).
     * Implement user profile basic information import from knack (rudaporto).
     * Update JobSync to import all comments using the new Comment format (rudaporto).
     * Create new functions to add user info to state_history and to get user info now from UserProfile model (rudaporto).
     * Added Order.assignment relationshit to return the last active Assignment of one Order (rudaporto).
     * Pin pyramid to version 1.7.3 (rudaporto).
     * Integrate briefy.common change on Timestamp.update_at (rudaporto).
     * Implement default filter for the Assignment that uses _custom_filter parameter to show Assignments avaiable in the Professional Pool.
     * Set AssignmentWorkflowService.enble_secutiry = False. Apply filter avoid Professional do self_assign one Assignment (rudaporto).
     * Improve Assingment workflow to set professional_user local role when self_assign or assign (rudaporto).
     * Improve LeicaBriefyRoles mixin: association proxy factory now can receive the list of permission to create the local role. (rudaporto).



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

