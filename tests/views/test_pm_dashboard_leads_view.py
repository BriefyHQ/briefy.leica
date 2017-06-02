"""Test PM Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestPMDashboardLeadsView(BaseDashboardTestView):
    """Test pm dashboard for Leads."""

    base_paths = (
        '/dashboards/pm/lead',
    )
