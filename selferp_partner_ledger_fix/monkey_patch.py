def monkey_patch(cls):
    """ Decorator for any function to patch method of given class

    :param cls:
    :return:
    """
    def decorate(f):
        name = f.__name__
        f.super = getattr(cls, name, None)
        setattr(cls, name, f)
        return f
    return decorate

