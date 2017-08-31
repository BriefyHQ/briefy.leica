"""Test Finance Dashboard Delivered view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestFinanceDashboardDeliveredView(BaseDashboardTestView):
    """Test finance dashboard for Delivered orders."""

    base_paths = (
        '/dashboards/finance/delivered',
    )
