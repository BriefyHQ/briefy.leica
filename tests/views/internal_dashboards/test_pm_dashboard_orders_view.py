"""Test PM Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestPMDashboardOrderView(BaseDashboardTestView):
    """Test pm dashboard for Orders."""

    base_paths = (
        '/dashboards/pm/order',
    )
