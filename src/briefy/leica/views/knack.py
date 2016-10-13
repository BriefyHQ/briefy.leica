"""Service to import/sync customers and dependencies from knack to briefy.leica."""
from briefy.leica import logger
from briefy.ws import CORS_POLICY
from briefy.ws.resources.factory import BaseFactory
from cornice.resource import resource
from cornice.resource import view
from pyramid.authentication import Everyone
from pyramid.authorization import Allow
from simplejson.scanner import JSONDecodeError

import colander


class KnackLoggerSchema(colander.MappingSchema):
    """Payload with data from knack to be logged."""
    payload = colander.Mapping()


class KnackLoggerFactory(BaseFactory):
    """Internal context factory for knack logger service."""

    @property
    def __base_acl__(self):
        """KnackLoggerFactory custom acl.

        :return list of acl for the current logged user plus defaults.
        :rtype list
        """
        return [
            (Allow, Everyone, ['add']),
        ]


@resource(path='/knack/logger',
          cors_policy=CORS_POLICY,
          schema=KnackLoggerSchema,
          factory=KnackLoggerFactory)
class KnackLoggerService:
    """Service to log payloads from knack."""

    def __init__(self, context, request):
        """Service initialize."""
        self.context = context
        self.request = request

    @view(permission='add')
    def post(self):
        """Get payload from knack, add user and referrer and sent to logger.info."""
        referrer = self.request.referrer
        user = self.request.user

        try:
            payload = self.request.json
        except JSONDecodeError as exc:
            msg = 'Invalid payload. Exception: {exc}'.format(exc=exc)
            logger.error(msg)
            return dict(status='error', message=msg)

        extra = dict(payload=payload, url=referrer)
        if user:
            extra['user'] = user.to_dict()
        logger.info('Knack payload', extra=extra)

        return {
            'status': 'success',
            'extra': extra
        }
