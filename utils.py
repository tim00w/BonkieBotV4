import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def hashed(func):
    def decorator(input):
        return func(hash(input))
    return decorator


def add_key(secret):
    def decorator(func):
        def real_decorator(input):
            return func(str(input) + secret)
        return real_decorator
    return decorator


def test1(val):
    return val


@hashed
def test2(val):
    return val


@add_key('abc')
def test3(val):
    return val


@add_key('abc')
@hashed
def test4(val):
    return val


@hashed
@add_key('abc')
def test5(val):
    return val


v = 'abc'
test1(v)
test2(v)
test3(v)
test4(v)
test5(v)