"""Test Customer Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestCustomerDashboardOrderView(BaseDashboardTestView):
    """Test customer dashboard for Orders."""

    base_paths = (
        '/dashboards/customer/order',
    )
