"""Test Professional Billing Info view."""
from briefy.leica import models
from conftest import BaseTestView

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalBillingInfo(BaseTestView):
    """Test Billing Info for an Asset."""

    base_path = (
        '/professionals/23d94a43-3947-42fc-958c-09245ecca5f2/billing'
    )
    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/professional_billing_infos.json'
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
