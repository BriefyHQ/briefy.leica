"""Scouting Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.models import OrderLocation
from briefy.leica.models import Professional
from briefy.leica.models import Project
from briefy.leica.models import WorkingLocation
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.sql import and_


total_professionals_per_country = select([
    WorkingLocation.country.label('country'),
    func.count(distinct(Professional.id)).label('professionals')
]).group_by(
    WorkingLocation.country
).where(
    Professional.id == WorkingLocation.professional_id
).alias('total_professionals_per_country')

total_assignments_per_country = select([
    OrderLocation.country.label('country'),
    func.count(distinct(Assignment.id)).label('total'),
    func.sum(
        case([(Assignment.state == 'pending', 1)], else_=0)
    ).label('unassigned'),
    func.sum(
        case([(
            and_(
                Assignment.pool_id.isnot(None),
                Assignment.state == 'published'
            ), 1)], else_=0)
    ).label('pool'),
    func.sum(
        case([(Assignment.state.in_(('assigned', 'scheduled')), 1)], else_=0)
    ).label('assigned'),
    total_professionals_per_country.c.professionals
]).group_by(
    OrderLocation.country,
    total_professionals_per_country.c.professionals
).where(
    and_(
        Assignment.order_id == Order.id,
        OrderLocation.order_id == Order.id,
        Assignment.location.has(country=OrderLocation.country),
        total_professionals_per_country.c.country == OrderLocation.country,
        # TODO: check if we should limit the search
        Assignment.state.in_(
            ('pending', 'published', 'assigned', 'scheduled')
        )
    )
).alias('total_assignments_per_country')


class DashboardScoutingCountry(Base):
    """Dashboard Scouting: Total of Assignments per country x state."""

    __table__ = total_assignments_per_country
    __mapper_args__ = {
        'primary_key': [total_assignments_per_country.c.country]
    }
    __session__ = Session


total_assignments_per_project = select([
    Project.title,
    func.count(distinct(Assignment.id)).label('total'),
    func.sum(
        case([(Assignment.state == 'pending', 1)], else_=0)
    ).label('unassigned'),
    func.sum(
        case([(
            and_(
                Assignment.pool_id.isnot(None),
                Assignment.state == 'published'
            ), 1)], else_=0)
    ).label('pool'),
    func.sum(
        case([(Assignment.state.in_(('assigned', 'scheduled')), 1)], else_=0)
    ).label('assigned'),
    func.count(distinct(Assignment.professional_id)).label('professionals'),
]).group_by(
    Project.title
).where(
    and_(
        Project.id == Order.project_id,
        Assignment.order_id == Order.id,
        Assignment.state.in_(
            ('pending', 'published', 'assigned', 'scheduled')
        )
    )
).alias('total_assignments_per_project')


class DashboardScoutingProject(Base):
    """Dashboard Scouting: Total of Assignments per Project."""

    __table__ = total_assignments_per_project
    __mapper_args__ = {
        'primary_key': [total_assignments_per_project.c.title]
    }
    __session__ = Session
