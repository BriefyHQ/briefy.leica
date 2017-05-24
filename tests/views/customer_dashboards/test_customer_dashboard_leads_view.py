"""Test Customer Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestCustomerDashboardLeadsView(BaseDashboardTestView):
    """Test customer dashboard for Leads."""

    base_paths = (
        '/dashboards/customer/lead',
    )
