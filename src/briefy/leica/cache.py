"""Initial briefy.leica cache configuration."""
from dogpile.cache import make_region


def model_key_generator(namespace, fn, **kw):
    """Generate keys for all models objects."""
    namespace = namespace or ''
    namespace = '{fname}{namespace}'.format(
        fname=fn.__name__,
        namespace=namespace,
    )

    def generate_key(*args):
        """Create unique key for each model using UID."""
        obj = args[0]
        name = obj.__class__.__name__
        key = '{name}.{namespace}-{id}'.format(
            name=name,
            namespace=namespace,
            id=obj.id,
        )
        return key

    return generate_key


region = make_region(
    function_key_generator=model_key_generator
).configure(
    'dogpile.cache.memory',
    expiration_time=3600,
)
