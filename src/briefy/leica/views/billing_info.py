"""Views to handle Customers creation."""
from briefy.leica.events import billing_info as billing_events
from briefy.leica.models import CustomerBillingInfo
from briefy.leica.models import ProfessionalBillingInfo
from briefy.ws import CORS_POLICY
from briefy.ws.resources import RESTService
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from pyramid.security import Allow


class CustomerBillingInfoFactory(BaseFactory):
    """CustomerBillingInfo context factory."""

    model = CustomerBillingInfo

    __base_acl__ = [
        (Allow, 'g:customers', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_bizdev', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_finance', ['create', 'list', 'view', 'edit']),
    ]


COLLECTION_PATH = '/billing_info/customers'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=CustomerBillingInfoFactory
)
class CustomerBillingInfoService(RESTService):
    """CustomerBillingInfo Service."""

    model = CustomerBillingInfo
    default_order_by = 'created_at'
    default_order_direction = -1

    _default_notify_events = {
        'POST': billing_events.CustomerBillingInfoCreatedEvent,
        'PUT': billing_events.CustomerBillingInfoUpdatedEvent,
        'GET': billing_events.CustomerBillingInfoLoadedEvent,
        'DELETE': billing_events.CustomerBillingInfoDeletedEvent,
    }


class ProfessionalBillingInfoFactory(BaseFactory):
    """ProfessionalBillingInfo context factory."""

    model = ProfessionalBillingInfo

    __base_acl__ = [
        (Allow, 'g:professionals', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_scout', ['create', 'list', 'view', 'edit']),
        (Allow, 'g:briefy_finance', ['create', 'list', 'view', 'edit']),
    ]


COLLECTION_PATH = '/billing_info/professionals'
PATH = COLLECTION_PATH + '/{id}'


@resource(
    collection_path=COLLECTION_PATH,
    path=PATH,
    cors_policy=CORS_POLICY,
    factory=ProfessionalBillingInfoFactory
)
class ProfessionalBillingInfoService(RESTService):
    """ProfessionalBillingInfo Service."""

    model = ProfessionalBillingInfo
    default_order_by = 'created_at'
    default_order_direction = -1

    _default_notify_events = {
        'POST': billing_events.ProfessionalBillingInfoCreatedEvent,
        'PUT': billing_events.ProfessionalBillingInfoUpdatedEvent,
        'GET': billing_events.ProfessionalBillingInfoLoadedEvent,
        'DELETE': billing_events.ProfessionalBillingInfoDeletedEvent,
    }
