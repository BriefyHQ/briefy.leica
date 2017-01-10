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


total_assignments_customer = select([
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
        case([(Order.state == 'in_qa', 1)], else_=0)
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
            ('received', 'assigned', 'scheduled', 'cancelled', 'delivered', 'accepted')
        ),
        Project.id == Order.project_id,
    )
).alias('total_assignments_professional')


class DashboardCustomerOrder(Base):
    """Dashboard Customer: Total of Order by workflow state."""

    __table__ = total_assignments_customer
    __mapper_args__ = {
        'primary_key': [total_assignments_customer.c.total]
    }
    __session__ = Session
