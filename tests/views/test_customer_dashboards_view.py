"""Test Customer Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestCustomerDashboardView(BaseDashboardTestView):
    """Test customer dashboards."""

    base_paths = (
        '/dashboards/customer/order',
    )
