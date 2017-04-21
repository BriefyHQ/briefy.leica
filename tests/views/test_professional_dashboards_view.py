"""Test Professional Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestProfessionalDashboardView(BaseDashboardTestView):
    """Test professional dashboards."""

    base_paths = (
        '/dashboards/professional/assignment',
    )
