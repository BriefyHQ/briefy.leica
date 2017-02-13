"""Test QA Dashboards view."""
import pytest

from conftest import BaseDashboardTestView


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestQaDashboardView(BaseDashboardTestView):
    """Test qa dashboards."""

    base_paths = (
        '/dashboards/qa/type',
        '/dashboards/qa/project',
    )
