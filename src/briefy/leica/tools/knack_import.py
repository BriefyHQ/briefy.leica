from briefy.leica import logger
from briefy.leica.config import DATABASE_URL
from briefy.leica.db import Session  # noQA
from briefy.leica.db import create_engine
from briefy.leica.models import Job as LJob
from briefy.leica.models import Project as LProject
from briefy.leica.models import Customer as LCustomer


import briefy.knack as K

import logging
import transaction

logger.setLevel(logging.DEBUG)
logger.handlers[0].setLevel(logging.DEBUG)


def configure():
    """Bind session for 'stand alone' DB usage"""
    global Session
    engine = create_engine(DATABASE_URL, pool_recycle=3600)
    Session.configure(bind=engine)
    return Session

def get_model_and_data(model_name):
    """Load model and data dump from Knack"""
    logger.info('Retrieving {0} model from Knack'.format(model_name))
    model = K.get_model(model_name)
    logger.info('Querying all existing {0}s'.format(model_name))
    all_items = model.query.all()
    logger.info('Fetched {0} {1}s from Knack'.format(len(all_items), model_name))
    return model, all_items


def main():
    """Handles all the bagaça"""
    Session = configure()  # noQA

    KProject, all_projects = get_model_and_data('Project')
    # KJob, all_jobs = get_model_and_data('Job')
    project_dict={}
    customer_dict={}
    count = 0
    for project in all_projects:
        if project.company[0]['id'] not in customer_dict:
            customer = LCustomer(external_id=project.company[0]['id'], display_name=project.company[0]['identifier'])
            Session.add(customer)
            customer_dict[customer.external_id] = customer
        else:
            customer = customer_dict['customer_id']

        lproject = LProject(customer=customer, external_id=project.id,
                            tech_requirements={'dimension': '4000x2000'})

        with transaction.manager:
            try:
                Session.add(lproject)
                Session.flush()
            except Exception as error:
                logging.error('Could not import project "{}". Error {}'.format(project.name, error))
                Session.rollback()
                continue

            count += 1
        project_dict[project.id] = project
    logging.info('{} new projects imported into Leica'.format(count))

if __name__ == '__main__':
    main()
