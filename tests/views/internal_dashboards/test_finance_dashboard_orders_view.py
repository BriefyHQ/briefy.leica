"""Test Finance Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestFinanceDashboardOrderView(BaseDashboardTestView):
    """Test Finance dashboard for Orders."""

    base_paths = (
        '/dashboards/finance/order',
    )
