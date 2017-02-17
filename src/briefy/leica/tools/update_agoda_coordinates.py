from briefy.leica.db import Session
from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.models import Order
from briefy.leica.sync import db
from sqlalchemy.orm.attributes import flag_modified

import csv
import transaction


def main(session):
    """Excute coordinates update."""
    agoda_file = open('src/briefy/leica/data/agoda.txt')
    reader = csv.DictReader(agoda_file, delimiter='\t', quoting=csv.QUOTE_NONE)

    for item in reader:
        latitude = float(item.get('hotel_latitude').replace(',', '.'))
        longitude = float(item.get('hotel_longitude').replace(',', '.'))
        customer_order_id = item.get('hotel_id')

        orders = session.query(Order).join(Project, Customer).filter(
            Order.project_id == Project.id,
            Project.customer_id == Customer.id,
            Order.customer_order_id == customer_order_id,
            Customer.id == 'd466091b-98c5-4f9d-81a6-ecbc83dd3386',
        ).all()

        for order in orders:
            location = order.location
            coordinates = {
                'type': 'Point',
                'coordinates': [longitude, latitude]
            }
            location.coordinates = coordinates
            flag_modified(location, '_coordinates')
            print('Added coordinates to Order: {order_id} -  Location: {location_id}'.format(
                order_id=customer_order_id,
                location_id=location.id
            ))
        transaction.commit()


if __name__ == '__main__':
    session = db.configure(Session)
    main(session)
