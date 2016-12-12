from briefy.leica.models import Customer
from briefy.leica.models import Project
from briefy.leica.sync import ModelSync
from briefy.leica.sync.customer import CustomerSync


class ProjectSync(ModelSync):
    """Syncronize Projects."""

    model = Project
    knack_model_name = 'Project'

    def get_customer(self, kobj):
        """Get Customer object for this Project."""
        customer_sync = CustomerSync(self.session)
        knack_company = customer_sync.get_knack_item(kobj.company[0]['id'])
        customer = Customer.query().filter_by(external_id=knack_company.id).one()
        return customer, knack_company

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for customer object."""
        result = super().get_payload(kobj, briefy_id)
        customer, company = self.get_customer(kobj)

        # TODO: Local roles and comments
        # 'clients_project_manager'
        # 'project_comment'

        try:
            if kobj.project_set_price:
                price = int(kobj.project_set_price * 100)
            else:
                price = 0
        except ValueError:
            price = 0

        result.update(
            dict(
                title=kobj.project_name.strip(),
                description=kobj.project_abstract,
                customer_id=customer.id,
                briefing=kobj.briefing,
                approval_window=kobj.set_refusal_window,
                availability_window=12,
                payout_currency=kobj.currency_set_price,
                payout_value=kobj.project_payout_set_price or 0,
                cancellation_window=kobj.cancellation_window or 0,
                project_manager=self.get_user(kobj, 'project_manager'),
                contract=company.link_to_contract.url,
                _price=price,
                price_currency=kobj.currency_set_price,
                external_id=kobj.id,
                release_template=kobj.release_template,
                # TODO: use ms.laure
                tech_requirements={'dimension': '4000x3000'}
            )
        )
        return result
