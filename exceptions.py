from contextlib import contextmanager

@contextmanager
def try_ignored(*exceptions):

    """ 
    usage;
    with try_ignored(Exception):
        funct(*arg, **kwarg)

    """
    try:
        yield
    except exceptions:
        print(f"{exceptions} occured; passing to next step")
        pass
