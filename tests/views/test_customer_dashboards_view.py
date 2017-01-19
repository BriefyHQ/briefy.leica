"""Test Customer Dashboards view."""
import pytest

from conftest import BaseDashboardTestView


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestCustomerDashboardView(BaseDashboardTestView):
    """Test customer dashboards."""

    base_paths = (
        '/dashboards/customer/order',
    )
