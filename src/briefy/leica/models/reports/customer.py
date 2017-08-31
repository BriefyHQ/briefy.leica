"""Customer Report models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Order
from briefy.leica.models import Project
from sqlalchemy import and_
from sqlalchemy import select


orders_project = select([
    Order.id.label('order_id'),
    Project.title.label('project_title'),
    Order._slug.label('briefy_id'),
    Order.customer_order_id.label('customer_order_id'),
    Order.title.label('title'),
    Order.state.label('state'),
    Order.created_at.label('created_at'),
    Order.scheduled_datetime.label('scheduled_datetime'),
    Order.deliver_date.label('deliver_date'),
    Order.timezone.label('timezone'),
    Order.accept_date.label('accept_date')
]).where(
    and_(
        Order.project_id == ':project_id',
        Order.project_id == Project.id,
        Project.local_roles.any(principal_id=':user_id')
    )
).order_by(
    Order.created_at.asc()
).alias('orders_project')


class OrdersByProjectReport(Base):
    """Report returning orders by a project."""

    __table__ = orders_project
    __mapper_args__ = {
        'primary_key': [orders_project.c.order_id]
    }
    __session__ = Session
