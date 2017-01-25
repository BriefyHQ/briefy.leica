"""Customer Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select


total_order_customer = select([
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
        case([(Order.state.in_(('in_qa', 'refused')), 1)], else_=0)
    ).label('in_qa'),
    func.sum(
        case([(Order.state == 'cancelled', 1)], else_=0)
    ).label('cancelled'),
    func.sum(
        case([(Order.state.in_(('delivered', 'accepted')), 1)], else_=0)
    ).label('completed'),
]).group_by(Project.title).where(
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
                'refused'
            )
        ),
        Project.id == Order.project_id,
        Project.local_roles.any(role_name='customer_user', user_id=':user_id')
    )
).alias('total_order_customer')


class DashboardCustomerOrder(Base):
    """Dashboard Customer: Total of Order by workflow state."""

    __table__ = total_order_customer
    __mapper_args__ = {
        'primary_key': [total_order_customer.c.total]
    }
    __session__ = Session
