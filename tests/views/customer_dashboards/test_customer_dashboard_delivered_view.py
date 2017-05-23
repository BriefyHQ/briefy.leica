"""Test Customer Dashboard Delivered view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestCustomerDashboardDeliveredView(BaseDashboardTestView):
    """Test customer dashboard for Delivered orders."""

    base_paths = (
        '/dashboards/customer/delivered',
    )
