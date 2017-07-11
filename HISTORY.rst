=======
History
=======

2.2.0 (Unreleased)
------------------

    * Remove scout_manager as a required field for Order.assign transition (rudaporto).
    * Added back external_id column to Professional model (rudaporto).
    * Update Professional tests to use the classmethod `created` to create new model instances (rudaporto).
    * Added tests for finance and bizdev dashboards and group all dashboards tests in a folder (rudaporto).
    * Removed the sqlalchemy continuum make_versioned call since this is already execute in briefy.common init (rudaporto).
    * Removed BillingInfo.title field and turn it to a computed field on first and last name (rudaporto).
    * Removed deprecated TaxInfo mixin from Customer model (rudaporto).
    * Clean up to_dict from all models that inherit from BaseMetadata since it will take care of adding these fields (rudaporto).
    * Remove all override code from BillingInfo and ProfessionalBillingInfo that is already in BaseMetadata now (rudaporto).
    * Remove Order.type field since Item.type is already used and Order.current_type should store the current order type (rudaporto).
    * Fix: UserProfile.owner actor colander definition should be a list (rudaporto).
    * Override UserProfile.title setter and getter to compute from first and last name and also update Item.title using an observer (rudaporto).
    * Avoiding to create or activate a new user in Rolleiflex internal API if running in test or development ENV (rudaporto).
    * Update description field on Image model payload (rudaporto).
    * Remove title from InternalUserProfile model payload (rudaporto).
    * Added asset_types field to LeadOrder model payload (rudaporto).
    * Remove title from Professional model payload (rudaporto).
    * Added database migration: (rudaporto)
        * migrate data to items and items_version
        * migrate external_id from userprofiles to professional (intercom still need it)
        * migrate local roles from the old table to the new table format
    * Final query to create localroles in the project level for internal_qa and internal_scout based on the assignments roles for each project. (rudaporto)
    * Move to postgresql 9.6 container (rudaporto).
    * Added __parent_attr__ attribute to the models: Project, Order, Assignment, Asset (rudaporto).
    * Added migration to update items.path using parent items.path (rudaporto).
    * Added observer to update Project, Order, Assignment and Asset path when foreign key to parent model changes (rudaporto).


2.1.26 (2017-07-04)
-------------------

    * Card #448: Give Support users permission to remove availability from Orders in Received state (ericof).

2.1.25 (2017-07-03)
-------------------

    * Card #434: Make sure Professional user has ownership over its profile (ericof).
    * Card #436: Conditional add order per project (ericof).
    * Fix /pools/{id}/history endpoint access (ericof).

2.1.24 (2017-06-29)
-------------------

    * Fix incorrect endpoint integration between Leica and Rolleiflex (ericof).

2.1.23 (2017-06-28)
-------------------

    * Fix listing assignments per Professional (ericof).

2.1.22 (2017-06-28)
-------------------

    * Card #438: Fix search assignments by project title (ericof).

2.1.21 (2017-06-26)
-------------------

    * Card #391: Implement new finance reports (ericof).

2.1.20 (2017-06-20)
-------------------

    * Added history endpoint for all first level models (rudaporto).
    * Refactor to user VersionsService base class from briefy.ws for Versions endpoints (rudaporto).
    * Added versions endpoint for all first level models with versions support (rudaporto).
    * Card #413: Remove state_history from listing and view serialisations (ericof).
    * Card #407: Sync between Leica User Profiles and Rolleiflex accounts (ericof).
    * Refactor workflows to be inside packages (ericof).

2.1.19 (2017-06-12)
-------------------

    * Card #282: Allow filtering Order/LeadOrder by type on /orders endpoint (ericof).
    * Card #196: Migrate Delivery Hero project Orders to LeadOrders (ericof).
    * Card #197: Migrate Agoda project Orders to LeadOrders (ericof).
    * Card #358: Set Agoda and Delivery Hero projects to order_type = 'leadorder' (ericof).
    * Card #283: New dashboard for customer: Leads (ericof).
    * Card #364: Fix leadorder confirm workflow transition to only create the assignment after creation (rudaporto).
    * Add new related filter to CustomerProfileService to be able to filter by customer or project (rudaporto).
    * Card #368: CustomerUserProfile.project_roles setter now correct remove or add projects based on the received list (rudaporto).
    * Card #231: Add Actual Order Price field to Order and LeadOrder(ericof).
    * Card #231: Add Actual Order Price to finance export (ericof).
    * Card #378: Fix serialization of an Assignment if set_type is None (ericof).
    * Integrate change in briefy.common to log when we create the cache region (rudaporto).
    * Card #377: Add Leads dashboard to PM (ericof).
    * Card #392: Remove dependencies to briefy.knack (ericof).


2.1.18 (2017-06-02)
-------------------

    * Card #385: fix order location field in the order payload after order creation (rudaporto).
    * Fix: professionals view tests now have a proper main_location in the original payload (rudaporto).
    * Fix: professionals main_location update test now is really updating the existing location (rudaporto).
    * Fix: professional to_dict to never return 'assets' and 'assignments' collections (rudaporto).


2.1.17 (2017-05-24)
-------------------

    * Card #362: add a comment to Order after workflow 'accept' transition using transition message (rudaporto).

2.1.16 (2017-05-24)
-------------------

    * Card #47: order.schedule_datetime should be in the payload after schedule transition (rudaporto).

2.1.15 (2017-05-22)
-------------------

    * Card #355: block approve from post processing when there is no archive url (rudaporto).

2.1.14 (2017-05-19)
-------------------

    * Card #338: fixed leica worker failure when assets were not copied but order should be moved back to delivered (rudaporto).

2.1.13 (2017-05-18)
-------------------

    * Added cache layer using briefy.common.cache utility (Project, Order, Assignment) to_listing_dict, to_summary and to_dict (rudaporto).
    * Configure default cache backend to redis (docker container also) and added invalidation in model creation and updated events (rudaporto).
    * Update Project, Order, Assignment to_dict signature to follow the original one (rudaporto).
    * Make sure we do not return Enum instances in the to_dict (always return the str value) (rudaporto).
    * Added a global config to easy switch off the cache system (rudaporto).
    * Fix: price_currency field was mistyped in Order.__summary_attributes__ (rudaporto).
    * Added location to Order.__summary_attributes__ (rudaporto).
    * Changed the way we get the last Order assignment in Order.to_dict (rudaporto).
    * Added update events to Project, Order and Assignment workflow (rudaporto).
    * Improve logging on function safe_workflow_trigger_transitions (rudaporto).
    * Added new subscriber for CommentCreatedEvent to invalidate Comment.entity after comment creation (rudaporto).
    * Fix: function create_new_assignment_from_order now send id in the payload and append new assignment in the Order.assignments (rudaporto).
    * Added invalidation in all tasks and worker actions after update objects since some events will not be fired without a request (rudaporto).
    * Implement Order.workflow.edit_location transition (rudaporto).
    * New model type: LeadOrder (rudaporto).
    * New field for Project to set the type of order the project will use: order or leadorder (rudaporto).
    * Change in the /orders endpoint to create Order or LeadOrder based in the Project setting (rudaporto).
    * New unittest to cover all transitions for the OrderWorkflow and fixes to permissions (rudaporto).
    * New unittest for LeadOrder model and transitions (rudaporto).
    * New unittest for LeadOrder view (/orders with different project) (rudaporto).
    * Documentation small fixes and new document for LeadOrder type (rudaporto).
    * Refactor Order workflow and subscribers to use order.assingmnets[-1] and not order.assignment (rudaporto).
    * New leadorder subscriber module to handle LeadOrder created, updated and workflow transitions (rudaporto).
    * Aded script to export professionals to a spreadsheet file (jsbueno).
    * Card #272: Add asset_types to Project, Order, Assignment (ericof).
    * Card #67: Add Comment support to Professional profile (ericof).
    * Change LeadOrder workflow to only create the assignment when the LeadOrder is confirmed (rudaporto).
    * Improve LeadOrder model unittests (rudaporto).
    * Card #273: Added new state to Assignment: post_processing (rudaporto).
    * Card #273: Added new transitions to move to and back in_qa to post_processing and to approve from post_processing (rudaporto).
    * Reclassify Report views to be marked as background tasks in newrelic agent (rudaporto).
    * Card #286: Added remove_confirmation transition to LeadOrder workflow (rudaporto).
    * Card #300: Enable Workflow transitions for CustomerUserProfile and BriefyUserProfile (ericof).
    * Card #293: Set asset_types value using Project value when adding new Order, LeadOrder and new Assignments (rudaoporto).
    * Support group also can move a Professional to deleted state (ericof).
    * Return asset_type on Project summary (ericof).
    * Card #302 Fix: Assignment duplication when create a new Order (rudaporto).
    * Card #322: Update leica worker to process delivery or archive not necessary to both at same time (rudaporto).
    * Adding event handlers to leica work to deal with messages from ms.laure post processing copying (rudaporto).
    * Card #330: fixed (briefy.ws) bug were unassign an Order will create a new assignment without submit transition (rudaporto).
    * Card #336: fixed leica worker approve_assignment action was not moving order from in_qa to delivered when copy did not happen (rudaporto).

2.1.12 (2017-04-28)
-------------------

    * Fix: new script remove the last transition from two orders and respective assignments (rudaporto).

2.1.11 (2017-04-28)
-------------------

    * Fix: Order.delivery field now has the correct colander type definition (rudaporto).

2.1.10 (2017-04-26)
-------------------

    * Card #263: New Projects will have default delivery config and update config in all current Projects (rudaporto).

2.1.9 (2017-04-25)
------------------

    * Card #260: Fix Google drive delivery and archive configuration in all Delivery Hero Projects (rudaporto).

2.1.8 (2017-04-21)
------------------

    * Usage of octopus.checkstyle for Flake8 (ericof).
    * Card #151: Added support groups to Order workflow edit_payout and compensation (rudaporto).
    * Upgrade packages: pyramid to 1.8.3 and cornice to 2.4.0 (rudaporto).
    * Pined briefy.common and briefy.ws to stable releases 2.0.0 (rudaporto).

2.1.7 (2017-04-19)
------------------

    * Card #142: Trigger events on Tasks execution (ericof).
    * Card #243 and #244: added new column to store a number of refuse transitions order and assignment have  (rudaporto).
    * Card #214: fix Orders and Assignments without scout manager (rudaporto).
    * Update the Dockerfile to use python 3.6.1 container and updated packages (rudaporto/ericof).

2.1.6 (2017-04-13)
------------------

    * New column added to orders.csv exported from finance_csv_export: delivery_sftp_link (rudaporto).
    * Fix: retract_rejection transition now also move Order to in_qa if still scheduled (rudaporto).

2.1.5 (2017-04-11)
------------------

    * Card #237: fix failure when try to view a cancelled Order (rudaporto).
    * Card #73: fix transition Assignment.workflow.assign to set the scout_manager (Order and Assignment) properly (rudaporto).
    * Card #230: Order.workflow.perm_reject now understand a special value ('null') for reason_additional_compensation that sets to None the value and also sets to zero (0) the additional_compensation of the old assignment (rudaporto).
    * Card #49: Update the comment rule when remove_schedule transition is executed from Assignment and Order (rudaporto).
    * Card #241: move helper functions to fix permissions from scripts to briefy.leica and add fix for Delivery Hero (rudaporto).
    * Card #114: scheduling_issues transition now requires an additional_message field that will be concatenated with the message field (rudaporto).

2.1.4 (2017-04-06)
------------------

    * Card #215: new script to export all transition history of Orders to a tsv file (rudaporto).
    * Card #218: default value for empty submission_path in the Assignment must be None (rudaporto).

2.1.3 (2017-04-05)
------------------

    * Card #184: new script to add missing transitions to Order and Assignments using Ophelie's data set (rudaporto).
    * Card #136: improve perm_refuse workflow transition of Order to create an internal note (Order) and complete the Assignment (rudaporto).

2.1.2 (2017-03-31)
------------------

    * Card #62: Order and Assignment comments for Unassign, Re-assign, New shoot and Re-shoot should be internal only (rudaporto).
    * Card #170: update new_shoot transition adding payout fields to be updated in the old assignment before complete (rudaporto).
    * Card #41: added new Order transition perm_reject to reject the assignment and create a new shoot for the Order (rudaporto).
    * Card #171: improve and fix Order reshoot transition do update payout values on the old assignment and copy old values to the new assignment (rudaporto).
    * Card #167: improve Assignment workflow transition retract_rejection to move from Awaiting Assets to In QA without resubmit (rudaporto).
    * Card #41: update Assignment perm_reject transition and subscriber since it will be now called only from the Order workflow (rudaporto).
    * Remove payout_currency from Order transitions new_shoot, perm_reject and reshoot (rudaporto).
    * When transitioning perm_reject or completed are executed on the Assignment, make sure that only create a comment to the creative if the user id a PM (rudaporto).

2.1.1 (2017-03-29)
------------------

    * Fix: remove_availability transition now create a new assignment before cancel the old one (rudaporto).
    * Fix: when QA approve a set, creative comment was not being created as a comment in the Assignment (rudaporto).
    * Card #132: Added new _custom_filter to Orders endpoint to be used by the 'Deliveries' tab in customer interface (rudaporto).
    * Card #128: New dashboard for Customer and PM: delivered (rudaporto).
    * Fix: perm_rejected transitions to edit payout and edit compensation typo in definition (rudaporto).
    * Card #155: Update All Orders dashboard for PM, Customer and Bizdev (rudaporto).
    * Card #157: Update Orders export csv with new label for each workflow state (rudaporto).

2.1.0 (2017-03-26)
------------------

    * New model: ProfessionalBillingInfo (ericof).
    * New endpoint: /billing_info/professionals/{id} (ericof).
    * New model: CustomerBillingInfo (ericof).
    * New endpoint: /billing_info/customers/{id} (ericof).
    * On Order creation set order price based on project default value (ericof).
    * UserProfile: Add field to handle messenger info (ericof).
    * Project: Change colander typ of tech_requirements and delivery to JSONType, thus allowing update from the frontend (ericof).
    * Assignment: to_dict serialization includes Project delivery information (jsbueno).
    * Documentation: Add new models, split database into 3 topics (ericof).


2.0.31 (2017-03-22)
-------------------

    * Assignment: PM and Scouters can schedule and re-schedule assignments in the past (ericof).


2.0.30 (2017-03-19)
-------------------

    * New endpoint to manage BriefyUserProfile (ericof).
    * Return internal and company name on listings for UserProfile classes (ericof).
    * Fix: Bug when activating a BriefyUserProfile (ericof).

2.0.29 (2017-03-16)
-------------------

    * Fix: Worker, on approve_assignment action, was not transitioning Orders that were nt copied on Ms.Laure (ericof).


2.0.28 (2017-03-15)
-------------------

    * Fix: Assignment was ignoring approve transition when updating customer_approval_date (ericof).
    * Feature: Internal endpoints /ms.ophelie/orders /ms.ophelie/assignments return the CSV report to be consumed by ms.ophelie (ericof).


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

