from functools import wraps


def authorization_level(package):
    """
    returns write, read or None
    """
    if package == "ant31/no":
        return None
    elif package == "w":
        return "write"
    else:
        return 'write'


def write_access(package):
    return (authorization_level(package) == 'write')


def read_access(package):
    return (authorization_level(package) is not None)


def check_access(mode):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            package = kwargs['package']
            if mode == "write":
                access = write_access(package)
            elif mode == "read":
                access = read_access(package)
            else:
                raise ValueError("unknow access mode: %s" % mode)
            if not access:
                raise RuntimeError("Non authorized to access: %s" % package)
            else:
                return function(*args, **kwargs)
        return wrapper
    return decorator


@check_access('read')
def read(package):
    print "ok"


@check_access('write')
def write(package):
    print "ok"


@check_access('bad')
def bad(package):
    print "bad"
