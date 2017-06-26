"""Test Ms. Ophelie Assignment reports view."""
from briefy.leica import models

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies')
class TestAssignmentReports:
    """Test assignment reports."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.Customer, 'data/customers.json'),
        (models.Project, 'data/projects.json'),
        (models.Order, 'data/orders.json'),
        (models.Assignment, 'data/assignments.json'),
    ]

    testdata = [
        ('all', 7, b'project_name', b'Project'),
        ('active', 3, b'project_name', b'Project 05'),
        ('qa', 3, b'project_name', b'Project 05'),
    ]

    @pytest.mark.parametrize('report,size,column,value', testdata)
    def test_get_report(self, app, report, size, column, value):
        """Test get a report."""
        request = app.get(f'/ms-ophelie/assignments/{report}', status=200)

        assert request.status_code == 200
        headers = request.headers
        assert headers['Content-Disposition'] == 'attachment; filename=assignments.csv'

        body = request.body
        lines = body.split(b'\n')
        assert len(lines) == size
        assert column in lines[0]
        assert value in lines[1]

    def test_get_report_not_found(self, app):
        """Test get a report."""
        request = app.get(f'/ms-ophelie/assignments/foo', status=404)
        assert request.status_code == 404
