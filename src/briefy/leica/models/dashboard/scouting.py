"""Scouting Dashboard models."""
from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.sql import and_

from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.models import OrderLocation
from briefy.leica.models import Professional

total_assignments_per_country = select([
    OrderLocation.country.label('country'),
    func.count(Assignment.id).label('total'),
    func.sum(
        case([(Assignment.state.in_(('pending', 'published')), 1)], else_='0')
    ).label('unassigned'),
    func.sum(
        case([(and_(
            Assignment.pool_id is not None,
            Assignment.state == 'published'
        ), 1)], else_='0')
    ).label('job_pool'),
    func.sum(
        case([(Assignment.state.in_(('assigned', 'scheduled')), 1)], else_='0')
    ).label('assigned'),
    select([func.count(Professional.id)]).where(
        Professional.locations.any(country=OrderLocation.country)
    ).label('professionals')
]).group_by(OrderLocation.country, 'professionals').where(
    and_(
        Assignment.order_id == Order.id,
        OrderLocation.order_id == Order.id,
        Assignment.state.in_(
            ('pending', 'published', 'assigned', 'scheduled')
        )
    )
).alias('total_assignments_per_country')


class DashboardScoutingCountry(Base):
    """Dashboard Scouting: Total of Assignments per country x state"""
    __table__ = total_assignments_per_country

    __mapper_args__ = {
        'primary_key': [total_assignments_per_country.c.country]
    }
    __session__ = Session
