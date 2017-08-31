"""Test Bizdev Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestBizdevDashboardOrderView(BaseDashboardTestView):
    """Test Bizdev dashboard for Orders."""

    base_paths = (
        '/dashboards/bizdev/order',
    )
