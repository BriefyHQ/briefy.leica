"""Finance Dashboard models."""
from briefy.leica.db import Base
from briefy.leica.db import Session
from briefy.leica.models.dashboard.base import total_order_project


class DashboardFinanceOrder(Base):
    """Dashboard Finance: Total of Order by workflow state."""

    __table__ = total_order_project
    __mapper_args__ = {
        'primary_key': [total_order_project.c.total]
    }
    __session__ = Session
