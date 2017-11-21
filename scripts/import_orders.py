"""Import orders from tsv files to Leica."""
from briefy.common.utils.data import Objectify
from briefy.leica.db import db_configure
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project
from pytz import country_timezones

import csv
import pycountry
import transaction
import uuid


BASE_PATH = 'scripts/data'

PROJECTS_TO_IMPORT = [
    {
        'file_name': 'booking-barcelona.tsv',
        'project': {
            'id': '4edab976-d299-422f-4f0d-16291b5693e7',
            'country': 'ES',
            'timezone': 'Europe/Madrid',
        },
        'imported': True,
    },
    {
        'file_name': 'booking-rio.tsv',
        'project': {
            'id': 'd51dc611-180c-4a27-03cf-513ce7df77ac',
            'country': 'BR',
            'timezone': 'America/Sao_Paulo',
        },
        'imported': True,

    },
    # change imported to False on all bellow items before commit
    {
        'file_name': 'holiday-lettings_north-america.tsv',
        'project': {
            'id': '08eb3ef6-ea26-4850-ac1d-d179949725dd',
            'country': 'US',
            'timezone': 'America/NewYork',  # TODO: get timezone from order location
        },
        'imported': True,

    },
    {
        'file_name': 'holiday-lettings_europe.csv',
        'project': {
            'id': 'c3142f54-19ee-4926-2d4a-02d32f40753d',
            'country': 'DE',
            'timezone': 'Europe/Central',  # TODO: get timezone from order location
        },
        'imported': True,
    },
    {
        'file_name': 'holiday-lettings_caribbean.tsv',
        'project': {
            'id': 'f3dfcd3f-94f8-4628-02f1-88245b732231',
            'country': 'PR',
            'timezone': 'America/Puerto_Rico',  # TODO: get timezone from order location
        },
        'imported': True,
    },
    {
        'file_name': 'holiday-lettings_africa.tsv',
        'project': {
            'id': 'a8cb3daa-3e7e-4acd-96a5-f3bf5c437fb7',
            'country': 'ZA',
            'timezone': 'Africa/Casablanca',  # TODO: get timezone from order location
        },
        'imported': True,
    },
    {
        'file_name': 'holiday-lettings_asia.tsv',
        'project': {
            'id': '5d2cbc76-b876-4a45-5499-deba9b795570',
            'country': 'ID',
            'timezone': 'Africa/Casablanca',
        },
        'imported': True,
    },
    {
        'file_name': 'doordash_project-monitor.tsv',
        'project': {
            'id': '413a0ebc-f2e0-4962-82aa-f03404c67ca7',
            'country': 'US',
            'timezone': 'America/NewYork',
        },
        'imported': True,
    },
    {
        'file_name': 'holiday-lettings_oceania.tsv',
        'project': {
            'id': '3af64007-9298-4fe5-f84d-17c3b898627a',
            'country': 'AU',
            'timezone': 'Australia/Sydney',
        },
        'imported': True,
    },
    {
        'file_name': 'opentable_project-monitoring.tsv',
        'project': {
            'id': 'd589c324-aa17-47a9-8b9b-59ab90550c34',
            'country': 'DE',
            'timezone': 'Europe/Central',
        },
        'imported': True,
    },
    {
        'file_name': 'traveloka_project-monitor.csv',
        'project': {
            'id': '296c3c3f-368f-470a-ac0f-2e80bec3c373',
            'country': 'ID',
            'timezone': 'Asia/Bangkok',
        },
        'imported': True,
    },
    {
        'file_name': 'justeat_london.csv',
        'project': {
            'id': '79fbb63a-77a0-456b-160f-41070bd816e9',
            'country': 'UK',
            'timezone': 'UTC',
        },
        'imported': True,
    },
    {
        'file_name': 'hostelworkd_50-properties-laura.csv',
        'project': {
            'id': '6ef17640-4175-4057-d90f-2c2f399b1637',
            'country': 'US',
            'timezone': 'America/NewYork',
        },
        'imported': True,
    },
    {
        'file_name': 'holiday-lettings_testimonial.csv',
        'project': {
            'id': '07ec7979-3b10-428c-0363-a9364933163a',
            'country': 'UK',
            'timezone': 'UTC',
        },
        'imported': True,
    },

]


class OrderImporter:
    """Import order from tsv file to leica."""

    def __init__(self, file_name: str, project: Objectify, session: Session):
        """Initialize order importer.

        :param file_name: file name with order records to be imported
        :param project: existing project ID to add the orders
        :param session: database session instance
        """
        self.file_name = file_name
        self.project = project
        self.session = session
        project = session.query(Project).get(project.id)
        self.project.customer_id = str(project.customer_id)

    @property
    def records(self):
        """Return records iterator from file."""
        file_name = f'{BASE_PATH}/{self.file_name}'
        delimiter = '\t' if file_name[-3:] == 'tsv' else ','
        with open(file_name, 'r') as fin:
            reader = csv.DictReader(fin, delimiter=delimiter)
            for item in reader:
                yield item

    def transform(self, record: dict) -> dict:
        """Transform data payload from tsv file to Order payload."""
        record = Objectify(record)
        project = self.project
        order_id = uuid.uuid4()

        number_required_assets = record._get('number_required_assets', 10)

        # parse first and last name
        names = record.full_name.split(' ')
        first_name = names[0]
        if len(names) > 1:
            last_name = ' '.join(names[0:])
        else:
            last_name = ''

        # parse country code based on the country name
        country = pycountry.countries.get(name=record.country.strip(' '))
        if not country:
            print(f'Country not found {record.country}')

        country = country.alpha_2 if country else project.country

        formatted_address = f'{record.address}, {record.district}, {record.locality}, ' \
                            f'{record.postal_code}, {project.country}'
        new_data = {
            'id': order_id,
            'project_id': project.id,
            'asset_types': ['Image'],
            'category': 'accommodation',
            'description': '',
            'title': record.title,
            'requirements': '',
            'current_type': 'order',
            'state': 'accepted',
            'number_required_assets': number_required_assets,
            'source': 'briefy',
            'customer_id': project.customer_id,
            'customer_order_id': record.customer_order_id,
            'price': 10000,  # TODO: use from project if exists
            'delivery': {
                'gdrive': record._get('download_link', '')
            },
            'price_currency': 'EUR',
            # TODO: use google maps api to get the geohash
            'location': {
                'id': uuid.uuid4(),
                'order_id': order_id,
                'state': 'created',
                'locality': record.locality,
                'country': country,
                'email': record.email,
                'formatted_address': formatted_address,
                'coordinates': [0, 0],
                'additional_phone': None,
                'timezone': country_timezones.get(country, [project.timezone])[0],
                'first_name': first_name,
                'last_name': last_name,
                'mobile': record.mobile,
                'info': {
                    'additional_info': '',
                    'province': record.locality,
                    'locality': record.locality,
                    'sublocality': record.district,
                    'route': record.address,
                    'street_number': '',
                    'country': project.country,
                    'postal_code': record.postal_code
                }
            },

        }
        return new_data

    def add(self, record: dict) -> Order:
        """Add a new order using record data."""
        data = self.transform(record)
        order = Order.create(data)
        print(f'Order "{order.title}" : {order.id} - imported.')
        self.session.add(order)
        return order

    def __call__(self):
        """Start the import process."""
        for record in self.records:
            self.add(record)


def main():
    """Execute import script."""
    for item in PROJECTS_TO_IMPORT:
        if not item.get('imported', False):
            session = db_configure(Session)
            importer = OrderImporter(
                item.get('file_name'),
                Objectify(item.get('project')),
                session
            )
            with transaction.manager:
                importer()


if __name__ == '__main__':
    main()
