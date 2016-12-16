from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'
    knack_parent_model = 'Company'
    parent_model = Customer

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for project object."""
        result = super().get_payload(kobj, briefy_id)
        customer, company = self.get_parent(kobj, 'company')

        # TODO: Local roles and comments
        # 'clients_project_manager'
        # 'project_comment'

        result.update(
            dict(
                title=kobj.project_name.strip(),
                description=kobj.project_abstract,
                customer_id=customer.id,
                briefing=kobj.briefing,
                approval_window=kobj.set_refusal_window,
                availability_window=12,
                payout_currency=kobj.currency_set_price or 'EUR',
                payout_value=self.parse_decimal(kobj.project_payout_set_price),
                cancellation_window=kobj.cancellation_window or 0,
                project_manager=self.get_user(kobj, 'project_manager'),
                contract=company.link_to_contract.url,
                price=self.parse_decimal(kobj.project_set_price),
                price_currency=kobj.currency_set_price or 'EUR',
                external_id=kobj.id,
                release_template=kobj.release_template,
                # TODO: use ms.laure
                tech_requirements={'dimension': '4000x3000'}
            )
        )
        return result
