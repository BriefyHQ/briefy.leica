"""Test PM Dashboard Delivered view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestPMDashboardDeliveredView(BaseDashboardTestView):
    """Test pm dashboard for Delivered orders."""

    base_paths = (
        '/dashboards/pm/delivered',
    )
