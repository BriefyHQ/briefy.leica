from dogpile.cache import make_region

def my_key_generator(namespace, fn, **kw):
    namespace = fn.__name__ + (namespace or '')

    def generate_key(*args):
        return namespace + '-' + str(args[0].id)

    return generate_key

region = make_region(
    function_key_generator = my_key_generator
).configure(
    'dogpile.cache.memory',
    expiration_time = 3600,
)
