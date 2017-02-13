"""Test Professional Dashboards view."""
import pytest

from conftest import BaseDashboardTestView


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestProfessionalDashboardView(BaseDashboardTestView):
    """Test professional dashboards."""

    base_paths = (
        '/dashboards/professional/assignment',
    )
