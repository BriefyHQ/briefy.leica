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
        case([(Assignment.state == 'awaiting_assets', 1)], else_=0)
    ).label('awaiting_submission_resubmission'),
    func.sum(
        case([(Assignment.state.in_(('in_qa', 'asset_validation')), 1)], else_=0)
    ).label('in_qa'),
    func.sum(
        case([(Assignment.state.in_(
            ('approved', 'completed', 'perm_rejected', 'cancelled', 'refused')
        ), 1)], else_=0)
    ).label('completed_inactive'),
]).where(
    and_(
        Assignment.state.in_(
            ('assigned', 'scheduled', 'in_qa', 'approved', 'completed',
             'perm_rejected', 'refused', 'cancelled', 'awaiting_assets', 'asset_validation')
        ),
        Assignment.professional_id == ':professional_id'
    )
).alias('total_assignments_professional')


class DashboardProfessionalAssignment(Base):
    """Dashboard Professional: Total of Assignments by workflow state."""

    __table__ = total_assignments_professional
    __mapper_args__ = {
        'primary_key': [total_assignments_professional.c.total]
    }
    __session__ = Session
