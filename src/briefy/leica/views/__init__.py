"""Common view functions."""
from briefy.ws.resources.factory import BaseFactory
from pyramid.security import Allow
from pyramid.security import Everyone


class InternalFactory(BaseFactory):
    """Internal resource context factory."""

    model = None

    @property
    def __base_acl__(self) -> list:
        """Hook to be use by subclasses to define default ACLs in context.
        :return: list of ACLs
        :rtype: list
        """
        _acls = [
            (Allow, Everyone, ['add', 'delete', 'edit', 'list', 'view'])
        ]
        return _acls
