"""Test Professional Billing Info view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalBillingInfo(BaseTestView):
    """Test Billing Info for an Asset."""

    base_path = (
        '/billing_info/professionals'
    )
    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/professional_billing_infos.json'
    ignore_validation_fields = ['professional', 'state_history']
    model = models.ProfessionalBillingInfo
    UPDATE_SUCCESS_MESSAGE = ''
    NOT_FOUND_MESSAGE = ''
    update_map = {
        'email': 'salgado@professional.briefy.co',
        'payment_info': [
            {
                'type_': 'paypal',
                'email': 'paypal@professional.briefy.co'
            }
        ]
    }
