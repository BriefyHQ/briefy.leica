"""Customer Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import types
from sqlalchemy.sql import expression


all_orders_customer = select([
    func.CONCAT('/projects/', expression.cast(Project.id, types.Unicode)).label('absolute_url'),
    Project.title,
    func.count(distinct(Order.id)).label('total'),
    func.sum(
        case([(Order.state == 'received', 1)], else_=0)
    ).label('received'),
    func.sum(
        case([(Order.state == 'assigned', 1)], else_=0)
    ).label('assigned'),
    func.sum(
        case([(Order.state == 'scheduled', 1)], else_=0)
    ).label('scheduled'),
    func.sum(
        case([(
            and_(
                Order.state == 'in_qa',
                Order.accept_date.is_(None)
            ), 1)], else_=0)
    ).label('in_qa'),
    func.sum(
        case([(Order.state == 'cancelled', 1)], else_=0)
    ).label('cancelled'),
    func.sum(
        case([(
            or_(
                and_(
                    Order.state.in_(('accepted', 'refused', 'perm_refused', 'in_qa')),
                    Order.accept_date.isnot(None)
                ),
                Order.state == 'delivered'
            ), 1)], else_=0)
    ).label('delivered'),
]).group_by(Project.title, Project.id).where(
    and_(
        Order.state.in_(
            (
                'received',
                'assigned',
                'scheduled',
                'cancelled',
                'delivered',
                'accepted',
                'in_qa',
                'refused',
                'perm_refused'
            )
        ),
        Project.id == Order.project_id,
        Project.local_roles.any(role_name='customer_user', user_id=':user_id'),
    )
).alias('all_orders_customer')


class DashboardCustomerAllOrders(Base):
    """Dashboard Customer: Total of Order by workflow state."""

    __table__ = all_orders_customer
    __mapper_args__ = {
        'primary_key': [all_orders_customer.c.absolute_url]
    }
    __session__ = Session


delivered_orders_customer = select([
    func.CONCAT('/projects/', expression.cast(Project.id, types.Unicode)).label('absolute_url'),
    Project.title,
    func.count(distinct(Order.id)).label('total'),
    func.sum(
        case([(
            and_(
                Order.state == 'delivered',
                Order.accept_date.is_(None)
            ), 1)], else_=0)
    ).label('newly-delivered'),
    func.sum(
        case([(
            and_(
                Order.state.in_(('refused', 'in_qa')),
                Order.accept_date.isnot(None)
            ), 1)], else_=0)
    ).label('further_revision'),
    func.sum(
        case([(
            and_(
                Order.state == 'delivered',
                Order.accept_date.isnot(None)
            ), 1)], else_=0)
    ).label('re-delivered'),
    func.sum(
        case([(Order.state == 'accepted', 1)], else_=0)
    ).label('completed'),
]).group_by(Project.title, Project.id).where(
    and_(
        or_(
            and_(
                Order.state.in_(('accepted', 'refused', 'perm_refused', 'in_qa')),
                Order.accept_date.isnot(None)
            ),
            Order.state == 'delivered'
        ),
        Project.id == Order.project_id,
        Project.local_roles.any(role_name='customer_user', user_id=':user_id')
    )
).alias('delivered_orders_customer')


class DashboardCustomerDeliveredOrders(Base):
    """Dashboard Customer: Delivered Orders by workflow state."""

    __table__ = delivered_orders_customer
    __mapper_args__ = {
        'primary_key': [delivered_orders_customer.c.absolute_url]
    }
    __session__ = Session
