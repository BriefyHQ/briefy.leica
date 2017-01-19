"""Test Scout Dashboards view."""
import pytest

from conftest import BaseDashboardTestView


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestScoutDashboardView(BaseDashboardTestView):
    """Test scout dashboards."""

    base_paths = (
        '/dashboards/scouting/country',
        '/dashboards/scouting/project',
        '/dashboards/scouting/pool',
    )
