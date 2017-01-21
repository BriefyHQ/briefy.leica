"""Import Professionals to Leica."""
from briefy.leica.models import BriefyUserProfile
from briefy.leica.models import CustomerUserProfile
from briefy.leica.sync import ModelSync
from briefy.leica.sync import PLACEHOLDERS


class UserProfileSync(ModelSync):
    """Syncronize user profiles."""

    # set in the subclass
    model = None
    knack_model_name = ''

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for a UserProfile object."""
        result = super().get_payload(kobj, briefy_id)
        first_name = kobj.name.first or PLACEHOLDERS['first_name']
        last_name = kobj.name.last or PLACEHOLDERS['last_name']
        state = 'active' if kobj.user_status == {'active'} else 'inactive'
        result.update(
            dict(
                state=state,
                email=kobj.email.email or PLACEHOLDERS['email'],
                first_name=first_name.strip(),
                last_name=last_name.strip(),
            )
        )
        return result


class BriefyUserProfileSync(UserProfileSync):
    """Syncronize BriefyUser profiles."""

    model = BriefyUserProfile
    # set in the subclass
    knack_model_name = ''

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for a UserProfile object."""
        payload = super().get_payload(kobj, briefy_id)
        payload.update(
            dict(company_name='Briefy')
        )
        return payload


class CustomerUserProfileSync(UserProfileSync):
    """Syncronize BriefyUser profiles."""

    model = CustomerUserProfile
    knack_model_name = 'Client'

    def get_payload(self, kobj, briefy_id=None):
        """Create payload for a UserProfile object."""
        payload = super().get_payload(kobj, briefy_id)
        # TODO: update other fields
        # payload.update(
        #    dict(company='Briefy')
        # )
        return payload


class ProjectManagerProfileSync(BriefyUserProfileSync):
    """Syncronize Project Manager profiles."""

    knack_model_name = 'ProjectManager'


class QAManagerProfileSync(BriefyUserProfileSync):
    """Syncronize QA Manager profiles."""

    knack_model_name = 'Qa'


class ScoutManagerProfileSync(BriefyUserProfileSync):
    """Syncronize Scout Manager profiles."""

    knack_model_name = 'ScoutingManager'


class FinanceManagerProfileSync(BriefyUserProfileSync):
    """Syncronize Finance Manager profiles."""

    knack_model_name = 'FinanceManager'


class AccountManagerProfileSync(BriefyUserProfileSync):
    """Syncronize Account Manager profiles."""

    knack_model_name = 'AccountManager'


class SupervisorProfileSync(BriefyUserProfileSync):
    """Syncronize Supervisor profiles."""

    knack_model_name = 'Supervisor'
