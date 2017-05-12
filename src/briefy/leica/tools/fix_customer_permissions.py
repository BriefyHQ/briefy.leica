"""Helpers to fix user permissions."""
from briefy.leica.db import Session
from briefy.leica.models import Customer
from briefy.leica.models import CustomerUserProfile
from briefy.leica.models import Order
from briefy.leica.models import Project
from briefy.leica.sync.db import configure

import transaction


def get_user_from_email(email):
    """Return Customer user from email."""
    return CustomerUserProfile.query().filter(
        CustomerUserProfile.email == email
    ).one_or_none()


def get_all_users_from_customer(customer):
    """Return all Customer users."""
    return CustomerUserProfile.query().filter(
        CustomerUserProfile.customer == customer
    ).all()


def fix_project_permissions(users, projects):
    """Add users to the customer_users in all projects."""
    for user in users:
        for project in projects:
            project.customer_users.append(user.id)
            for order in project.orders:
                order.customer_users.append(user.id)


def fix_customers_and_project_permissions(users, customer_id, projects=(), all_projects=False):
    """Add users to the customer_users in customers and projects."""
    customer = Customer.get(customer_id)
    user_ids = set([user.id for user in users])
    customer_users = set(customer.customer_users)
    diff = user_ids - customer_users
    msg = 'Customer {id}. Adding users: {users}'
    print(msg.format(id=customer.id, users=diff))
    customer.customer_users.extend(diff)
    if all_projects and not projects:
        projects = customer.projects
    project_ids = [project.id for project in projects]
    for project_id in project_ids:
        project = Project.get(project_id)
        title = project.title
        customer_users = set(project.customer_users)
        diff = user_ids - customer_users
        msg = 'Project {id}. Adding users: {users}'
        print(msg.format(id=project.id, users=diff))
        project.customer_users.extend(diff)
        orders = []
        for i, order in enumerate(project.orders):
            orders.append((i, order.id))
        for i, order_id in orders:
            order = Order.get(order_id)
            customer_users = set(order.customer_users)
            diff = user_ids - customer_users
            msg = 'Project: {title} Item: {item} Order {id}. Adding users: {users}'
            print(msg.format(id=order.id, users=diff, item=i, title=title))
            order.customer_users.extend(diff)
            if i % 10:
                transaction.commit()


def fix_all_customers():
    """Fix all customer permissions."""
    customers = [c.id for c in Customer.query().all()]
    for customer_id in customers:
        customer = Customer.get(customer_id)
        projects = customer.projects
        users = [CustomerUserProfile.get(u) for u in customer.customer_users]
        fix_customers_and_project_permissions(users, customer_id, projects)


def fix_just_eat_permissions():
    """Fix Just Eat permissions."""
    emails = [
        'chris.fordham@just-eat.co.uk'
    ]
    users = []
    for email in emails:
        user = get_user_from_email(email)
        users.append(user)

    customer_id = 'd36729f1-7879-4398-8f85-c579e1031250'
    customer = Customer.get(customer_id)
    projects = customer.projects
    fix_customers_and_project_permissions(users, customer_id, projects)


def fix_wolt_permissions():
    """Fix Wolt permissions."""
    emails = [
        'julia.ruottinen@wolt.com',
        'aku.kallonen@wolt.com',
        'jens.lund@wolt.com',
        'jessie@wolt.com'
    ]
    users = []
    for email in emails:
        user = get_user_from_email(email)
        users.append(user)

    customer_id = '11928c11-6b81-4a91-9f03-27772ad53d72'
    customer = Customer.get(customer_id)
    projects = customer.projects
    fix_customers_and_project_permissions(users, customer_id, projects)


def fix_ehvisio_permissions():
    """Fix eH Vision permissions."""
    customer_id = '83006d14-c78b-4969-9624-c1b704897877'
    customer = Customer.get(customer_id)
    projects = customer.projects
    users = [CustomerUserProfile.get(u) for u in customer.customer_users]
    fix_customers_and_project_permissions(users, customer_id, projects)


def fix_agoda_permissions():
    """Fix Agoda permissions."""
    emails = [
        'sarawadee.jiramaroota@agoda.com',
        'naruemon.somnam@agoda.com',
        'ornphicha.chawankul@agoda.com',
        'nasita.lobunchongsook@agoda.com',
        'pemika.yoothong@agoda.com',
        'phurin.paina@agoda.com',
        'nattharin.boutthong@agoda.com',
        'danie.montenegro@agoda.com',
        'kitty.qiu@agoda.com',
        'nasita.lobunchongsook@agoda.com',
        'naina.chugh@agoda.com',
        'nina.suthamjariya@agoda.com'
    ]
    users = []
    for email in emails:
        user = get_user_from_email(email)
        users.append(user)

    customer_id = 'd466091b-98c5-4f9d-81a6-ecbc83dd3386'
    customer = Customer.get(customer_id)
    projects = customer.projects

    fix_customers_and_project_permissions(users, customer_id, projects)


def fix_delivery_hero_permissions():
    """Fix Delivery Hero permissions."""
    emails = [
        'pia.jentgens@deliveryhero.com'
    ]
    users = []
    for email in emails:
        user = get_user_from_email(email)
        users.append(user)

    customer_id = '26cd8552-753c-4ff1-b413-74d61804e9bb'
    customer = Customer.get(customer_id)
    projects = customer.projects

    fix_customers_and_project_permissions(users, customer_id, projects)


if __name__ == '__main__':
    # just setup the database but run without transaction manager
    configure(Session)

    # fix permissions
    # fix_delivery_hero_permissions()
    # fix_just_eat_permissions()
    # fix_wolt_permissions()
    # fix_ehvisio_permissions()
    # fix_agoda_permissions()

    transaction.commit()
