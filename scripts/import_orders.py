"""Import orders from tsv files to Leica."""
from briefy.common.utils.data import Objectify
from briefy.leica.db import db_configure
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project

import csv
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
        }
    },
    {
        'file_name': 'booking-rio.tsv',
        'project': {
            'id': 'd51dc611-180c-4a27-03cf-513ce7df77ac',
            'country': 'BR',
            'timezone': 'America/Sao_Paulo',
        }

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
        with open(file_name, 'r') as fin:
            reader = csv.DictReader(fin, delimiter='\t')
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

        formatted_address = f'{record.address}, {record.district}, {record.country}, ' \
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
                'country': project.country,
                'email': record.email,
                'formatted_address': formatted_address,
                'coordinates': [0, 0],
                'additional_phone': None,
                'timezone': project.timezone,
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
