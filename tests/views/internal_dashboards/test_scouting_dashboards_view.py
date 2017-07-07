"""Test Scout Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestScoutDashboardView(BaseDashboardTestView):
    """Test scout dashboards."""

    base_paths = (
        '/dashboards/scouting/country',
        '/dashboards/scouting/project',
        '/dashboards/scouting/pool',
    )
