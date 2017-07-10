"""Test Ms. Ophelie Customer reports view."""
from briefy.leica import models

import pytest


@pytest.mark.usefixtures('db_transaction', 'create_dependencies')
class TestCustomerReports:
    """Test customer reports."""

    dependencies = [
        (models.InternalUserProfile, 'data/internal_profiles.json'),
        (models.Customer, 'data/customers.json'),
        (models.CustomerBillingInfo, 'data/customer_billing_infos.json'),
    ]

    testdata = [
        ('all', 7, b'customer_display_name', b'Client'),
    ]

    @pytest.mark.parametrize('report,size,column,value', testdata)
    def test_get_report(self, app, report, size, column, value):
        """Test get a report."""
        request = app.get(f'/ms-ophelie/customers/{report}', status=200)

        assert request.status_code == 200
        headers = request.headers
        assert headers['Content-Disposition'] == 'attachment; filename=customers.csv'

        body = request.body
        lines = body.split(b'\n')
        assert len(lines) == size
        assert column in lines[0]
        assert value in lines[1]
