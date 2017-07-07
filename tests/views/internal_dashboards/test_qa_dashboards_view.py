"""Test QA Dashboards view."""
from conftest import BaseDashboardTestView

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies', 'login')
class TestQaDashboardView(BaseDashboardTestView):
    """Test qa dashboards."""

    base_paths = (
        '/dashboards/qa/type',
        '/dashboards/qa/project',
    )
