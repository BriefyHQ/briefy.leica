"""Test Ms. Ophelie Professional reports view."""
from briefy.leica import models

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies')
class TestProfessionalReports:
    """Test professional reports."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
        (models.ProfessionalBillingInfo, 'data/professional_billing_infos.json'),
    ]

    testdata = [
        ('all', 5, b'professional_display_name', b' Salgado'),
    ]

    @pytest.mark.parametrize('report,size,column,value', testdata)
    def test_get_report(self, app, report, size, column, value):
        """Test get a report."""
        request = app.get(f'/ms-ophelie/professionals/{report}', status=200)

        assert request.status_code == 200
        headers = request.headers
        assert headers['Content-Disposition'] == 'attachment; filename=professionals.csv'

        body = request.body
        lines = body.split(b'\n')
        assert len(lines) == size
        assert column in lines[0]
        assert value in lines[1]
