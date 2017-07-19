"""Test PM Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestBizDevDashboardOrdersView(BaseDashboardTestView):
    """Test bizdev dashboard for Orders."""

    base_paths = (
        '/dashboards/bizdev/order',
    )
