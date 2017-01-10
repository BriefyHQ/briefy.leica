"""QA Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from briefy.leica.models import Order
from briefy.leica.models import Project
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.sql import and_


total_assignments_in_qa_type = select([
    func.count(distinct(Assignment.id)).label('total'),
    func.sum(
        case([(Assignment.set_type == 'refused_customer', 1)], else_=0)
    ).label('refused_customer'),
    func.sum(
        case([(Assignment.set_type == 'returned_photographer', 1)], else_=0)
    ).label('returned_photographer'),
    func.sum(
        case([(Assignment.set_type == 'new', 1)], else_=0)
    ).label('new'),
]).where(Assignment.state == 'in_qa').alias('total_assignments_in_qa_type')


class DashboardQaType(Base):
    """Dashboard Qa: Total of Assignments in_qa by type."""

    __table__ = total_assignments_in_qa_type
    __mapper_args__ = {
        'primary_key': [total_assignments_in_qa_type.c.total]
    }
    __session__ = Session


total_assignments_in_qa_project = select([
    Project.title,
    func.sum(
        case([(Assignment.set_type == 'refused_customer', 1)], else_=0)
    ).label('refused_customer'),
    func.sum(
        case([(Assignment.set_type == 'returned_photographer', 1)], else_=0)
    ).label('returned_photographer'),
    func.sum(
        case([(Assignment.set_type == 'new', 1)], else_=0)
    ).label('new'),
    func.count(distinct(Assignment.id)).label('total'),
]).group_by(Project.title).where(
    and_(
        Project.id == Order.project_id,
        Assignment.order_id == Order.id,
        Assignment.state == 'in_qa',
    )
).alias('total_assignments_in_qa_project')


class DashboardQaProject(Base):
    """Dashboard Qa: Total of Assignments in_qa by Project and Type."""

    __table__ = total_assignments_in_qa_project
    __mapper_args__ = {
        'primary_key': [total_assignments_in_qa_project.c.title]
    }
    __session__ = Session
