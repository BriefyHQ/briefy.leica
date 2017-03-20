"""Test Professional Billing Info database model."""
from briefy.leica import models
from conftest import BaseModelTest

import pytest


@pytest.mark.usefixtures('create_dependencies')
class TestProfessionalBillingInfoModel(BaseModelTest):
    """Test ProfessionalBillingInfo."""

    dependencies = [
        (models.Professional, 'data/professionals.json'),
    ]
    file_path = 'data/professional_billing_infos.json'
    model = models.ProfessionalBillingInfo

    def test_primary_payment_method(self, instance_obj):
        """Check if primary_payment_method is correctly retrieved."""
        primary_payment_method = instance_obj.primary_payment_method
        assert primary_payment_method == 'paypal'

        instance_obj.primary_payment_info = None
        primary_payment_method = instance_obj.primary_payment_method
        assert primary_payment_method == ''

    def test_secondary_payment_method(self, instance_obj):
        """Check if secondary_payment_method is correctly retrieved."""
        secondary_payment_method = instance_obj.secondary_payment_method
        assert secondary_payment_method == 'bank_account'

        instance_obj.secondary_payment_info = None
        secondary_payment_method = instance_obj.secondary_payment_method
        assert secondary_payment_method == ''
