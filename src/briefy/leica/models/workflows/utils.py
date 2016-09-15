from pyramid.security import Allow
from pyramid.security import Everyone


# TODO: Move this to briefy.ws

def with_workflow(workflow):
    """ Class  decorator that will attach a briefy_workflow to a model class

    No tonly this sets the correct workflow attribute on the class,
    but it also injects an __acl_ method on the the model class that is conformant
    to Pyramid's  ACLAuthorizationPolicy --

    it respects any __acl__ already on the class, but they are _appended_ with any permissions
    set on the Workflow defined States -
    Since those permissions are calculated
    dynamically when a context is retrieved, any permissions are added with
    (Allow, Everyone, permission_value) -- as the dynamic permission itself
    should have already taken in account the current user_id calculated

    """

    original_acl = None

    def __acl__(self):
        """ Callable that will replace the __acl__ attribute on the
            model class with one that will append the dynamic permissions
            calculated by the briefy workflow
        """
        # Call all 'Permission' objects on the Workflow

        # TODO: <provisional>
        if callable(original_acl):
            results = original_acl(self)
        else:
            # Makes a copy and forces the resulting iterable to be a list:
            results = list(original_acl)

        results.extend(
            (Allow, Everyone, permission) for permission in self.workflow.permissions()
        )

        return results

    def inner(cls):
        nonlocal original_acl, __acl__
        original_acl = getattr(cls, '__acl__', [])
        cls.__acl__ = __acl__
        # TODO: Review following line
        # cls._workflow = workflow_cls
        return cls

    return inner
