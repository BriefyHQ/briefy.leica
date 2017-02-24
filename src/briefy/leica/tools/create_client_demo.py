"""Script to setup a new environment for demo purpose."""
from briefy.common.types import BaseUser
from briefy.common.utils.data import generate_slug
from briefy.leica.db import Session
from briefy.leica.models import Customer
from briefy.leica.models import CustomerBillingAddress
from briefy.leica.models import CustomerUserProfile
from briefy.leica.models import Project
from briefy.leica.models import Order
from briefy.leica.sync import db

import transaction

PROJECT_MANAGER = '9df18a79-44dc-4c2f-86aa-09bf7706ae86'
CUSTOMER_USER = '4111d75b-19be-4a43-ad8a-3cd0fe854228'


class SetupDemo:
    """Manage the demo creation."""

    def __init__(self, session):
        """Create new demo."""
        self.session = session
        self.customer = None
        self.customer_user = None
        self.projects = []
        self.user = BaseUser(
            user_id=PROJECT_MANAGER,
            data={
                "locale": "en_GB",
                "fullname": "Erico Andrei",
                "first_name": "Erico",
                "email": "erico@briefy.co",
                "last_name": "Andrei",
                "groups": [
                    "g:briefy_pm",
                    "g:briefy_qa",
                    "g:briefy_bizdev",
                    "g:briefy_finance",
                    "g:briefy_scout",
                    "g:system"
                ]
            }
        )

    def add_customer(self):
        """Add new customer object."""
        title = 'Booking.com'
        payload = dict(
            slug=generate_slug(title),
            title=title,
            legal_name='Booking.com B.V.',
            tax_id='NL805734958B01',
            tax_country='NL',
            tax_id_type='VAT'
        )
        customer = Customer(**payload)
        self.session.add(customer)
        self.session.flush()
        wf = customer.workflow
        wf.context = self.user
        wf.submit()
        self.customer = customer

    def add_customer_address(self):
        """Add customer address."""
        formatted_address = 'Herengracht 597, 1017 CE Amsterdam, Netherlands'
        locality = 'Amsterdam'
        extra_location_info = {
            'coordinates': {
                'type': 'Point',
                'coordinates': [4.898530299999948, 52.3655292]
            }
        }
        info = dict(
            formatted_address=formatted_address,
            province='Netherlands',
            locality=locality,
            route='Herengracht',
            street_number='597',
            country='NL',
            postal_code='1017 CE'
        )
        data = dict(
            country='ML',
            formatted_address=formatted_address,
            info=info,
            locality=locality,
            timezone='CET',
            **extra_location_info
        )

        customer = self.customer
        data['customer_id'] = customer.id
        location = CustomerBillingAddress(**data)
        self.session.add(location)
        self.session.flush()
        customer.addresses.append(location)

    def add_customer_user(self):
        """Add a new user from the customer."""
        payload = dict(
            id=CUSTOMER_USER,
            email='martijn.savenije@booking.com',
            first_name='Martijn',
            last_name='Savenije',
            company_name='Booking.com',
            customer_roles=self.customer.id,
            owner=CUSTOMER_USER,
        )
        savepoint = transaction.savepoint()
        try:
            profile = CustomerUserProfile(**payload)
            self.session.add(profile)
            self.session.flush()
        except Exception as exc:
            savepoint.rollback()
            self.customer_user = CustomerUserProfile.get(CUSTOMER_USER)
        else:
            self.customer_user = profile
            try:
                wf = profile.workflow
                wf.context = self.user
                wf.activate()
            except Exception as exc:
                savepoint.rollback()
                profile.state = 'active'

    def add_projects(self):
        """Add all projects."""
        currency = 'EUR'
        category = 'accommodation'
        title_bali = 'Bali Hotels'
        title_bangkok = 'Bangkok Hotels'
        projects = [
            dict(
                slug=generate_slug(title_bali),
                title=title_bali,
                category=category,
                description='',
                abstract=None,
                customer_id=self.customer.id,
                briefing=None,
                approval_window=20,
                number_required_assets=10,
                availability_window=0,
                payout_currency=currency,
                payout_value=8000,
                cancellation_window=0,
                contract=None,
                price=10000,
                price_currency=currency,
                release_template=None,
                tech_requirements=None,
                project_manager=PROJECT_MANAGER,
                customer_user=CUSTOMER_USER
            ),
            dict(
                slug=generate_slug(title_bangkok),
                title=title_bangkok,
                category=category,
                description='',
                abstract=None,
                customer_id=self.customer.id,
                briefing=None,
                approval_window=20,
                number_required_assets=10,
                availability_window=0,
                payout_currency=currency,
                payout_value=8000,
                cancellation_window=0,
                contract=None,
                price=10000,
                price_currency=currency,
                release_template=None,
                tech_requirements=None,
                project_manager=PROJECT_MANAGER,
                customer_user=CUSTOMER_USER
            ),
        ]
        for item in projects:
            project = Project(**item)
            self.session.add(project)
            self.projects.append(project)
            session.flush()
            wf = project.workflow
            wf.context = self.user
            wf.start()

    def create_order(self, other, project):
        """Create new order based on another one."""
        payload = dict(
            title=other.title,
            description='',
            project_id=project.id,
            customer_id=project.customer.id,
            price=project.price,
            customer_order_id='BCOM-' + other.customer_order_id,
            price_currency=project.price_currency,
            requirements='Photos from Lobby, Pool and front-desk',
            number_required_assets=20,
            source='briefy',
            project_manager=PROJECT_MANAGER,
            customer_user=self.customer_user.id
        )
        order = Order(**payload)
        self.session.add(order)
        self.session.flush()
        wf = order.workflow
        wf.context = self.user
        wf.submit()
        location = other.location
        if location:
            location.order_id = order.id
        from briefy.leica.subscribers.utils import create_new_assignment_from_order
        create_new_assignment_from_order(order, None)

    def create_all_orders(self):
        """Create new orders in the project."""
        bali_orders = Order.query().join(Project).filter(
            Project.id == '1dafb433-9431-4295-a349-92c4ad61c59e',
            Order.state == 'received',
        )[:10]
        bangkok_orders = Order.query().join(Project).filter(
            Project.id == '2edf1e7b-b7f0-4ca4-8d1b-9a8baf05662c',
            Order.state == 'received',
        )[:10]

        bali_project, bangkok_project = self.projects

        for item in bali_orders:
            self.create_order(item, bali_project)

        for item in bangkok_orders:
            self.create_order(item, bangkok_project)

    def __call__(self):
        """Run the setup."""
        self.add_customer()
        self.add_customer_address()
        self.add_customer_user()
        self.add_projects()
        self.create_all_orders()


if __name__ == '__main__':
    session = db.configure(Session)
    with transaction.manager:
        setup = SetupDemo(session)
        setup()
