"""Professional Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models import Assignment
from sqlalchemy import case
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import and_


total_assignments_professional = select([
    func.count(distinct(Assignment.id)).label('total'),
    func.sum(
        case([(Assignment.state == 'assigned', 1)], else_=0)
    ).label('assigned'),
    func.sum(
        case([(Assignment.state == 'scheduled', 1)], else_=0)
    ).label('scheduled'),
    func.sum(
        case([(
            and_(
                Assignment.state == 'in_qa',
                Assignment.set_type == 'new'
            ), 1)], else_=0)
    ).label('in_qa'),
    func.sum(
        case([(
            and_(
                Assignment.state == 'awaiting_assets',
                Assignment.set_type == 'refused_customer'
            ), 1)], else_=0)
    ).label('rejected'),
    func.sum(
        case([(Assignment.state.in_(('approved', 'completed')), 1)], else_=0)
    ).label('completed'),
]).where(
    and_(
        Assignment.state.in_(
            ('assigned', 'scheduled', 'in_qa', 'approved', 'completed')
        ),
        Assignment.professional_id == ':professional_id '
    )
).alias('total_assignments_professional')


class DashboardProfessionalAssignment(Base):
    """Dashboard Professional: Total of Assignments by workflow state."""

    __table__ = total_assignments_professional
    __mapper_args__ = {
        'primary_key': [total_assignments_professional.c.total]
    }
    __session__ = Session
