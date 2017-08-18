"""PM Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Customer
from briefy.leica.models import LeadOrder
from briefy.leica.models import Order
from briefy.leica.models import Project
from briefy.leica.models.dashboard.base import total_order_project
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import types
from sqlalchemy.sql import expression


class DashboardPMOrder(Base):
    """Dashboard PM: Total of Order by workflow state."""

    __table__ = total_order_project
    __mapper_args__ = {
        'primary_key': [total_order_project.c.absolute_url]
    }
    __session__ = Session


delivered_orders_pm = select([
    func.CONCAT('/projects/', expression.cast(Project.id, types.Unicode)).label('absolute_url'),
    Project.title,
    func.count(distinct(Order.id)).label('total'),
    func.sum(
        case([(
            and_(
                Order.state == 'delivered',
                Order.accept_date.is_(None)
            ), 1)], else_=0)
    ).label('newly_delivered'),
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
    ).label('re_delivered'),
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
        Project.can_view.in_(['{internal_pm}']),
        or_(
            Project.local_roles.any(principal_id=':user_id'),
            Customer.local_roles.any(principal_id=':user_id')
        )
    )
).alias('delivered_orders_pm')


class DashboardPMDeliveredOrders(Base):
    """Dashboard PM: Delivered Orders by workflow state."""

    __table__ = delivered_orders_pm
    __mapper_args__ = {
        'primary_key': [delivered_orders_pm.c.absolute_url]
    }
    __session__ = Session


all_leads_pm = select(
    [
        func.CONCAT('/projects/', expression.cast(Project.id, types.Unicode)).label('absolute_url'),
        Project.title,
        func.count(distinct(LeadOrder.id)).label('total'),
        func.sum(case([(LeadOrder.state == 'new', 1)], else_=0)).label('open'),
        func.sum(case([(LeadOrder.state == 'cancelled', 1)], else_=0)).label('cancelled'),
        func.sum(case([(LeadOrder.state.notin_(['new', 'cancelled']), 1)], else_=0)).label(
            'confirmed'
        ),
    ]
).group_by(
    Project.title,
    Project.id
).where(
    and_(
        LeadOrder.state.in_(
            (
                'new',
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
        Project.order_type == 'leadorder',
        LeadOrder.id == Order.id,
        Project.can_view.in_(['{internal_pm}']),
        or_(
            Project.local_roles.any(principal_id=':user_id'),
            Customer.local_roles.any(principal_id=':user_id')
        )
    )
).alias('all_leads_pm')


class DashboardPMAllLeads(Base):
    """Dashboard PM: Total of Leads by workflow state."""

    __table__ = all_leads_pm
    __mapper_args__ = {
        'primary_key': [all_leads_pm.c.absolute_url]
    }
    __session__ = Session
