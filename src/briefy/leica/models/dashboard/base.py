"""Base Dashboard models for Briefy."""
from briefy.leica.models import Customer
from briefy.leica.models import Order
from briefy.leica.models import Project
from sqlalchemy import and_, or_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import types
from sqlalchemy.sql import expression


total_order_project = select([
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
        case([(Order.state.in_(('in_qa', 'refused')), 1)], else_=0)
    ).label('in_qa'),
    func.sum(
        case([(Order.state == 'cancelled', 1)], else_=0)
    ).label('cancelled'),
    func.sum(
        case([(Order.state.in_(('delivered', 'accepted')), 1)], else_=0)
    ).label('completed'),
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
                'refused'
            )
        ),
        Project.id == Order.project_id,
        Project.state == 'ongoing',
        Project.customer_id == Customer.id,
        or_(
            Project.local_roles.any(user_id=':user_id', can_view=True),
            Customer.local_roles.any(user_id=':user_id', can_view=True)
        )
    )
).alias('total_order_project')
