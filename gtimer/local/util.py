

def sanitize_rgstr_stamps(rgstr_stamps):
    if not isinstance(rgstr_stamps, (list, tuple)):
        raise TypeError("Expected list or tuple for rgstr_stamps (elements passed through str()).")
    rgstr_stamps = list(set(rgstr_stamps))
    for s in rgstr_stamps:
        s = str(s)
    return rgstr_stamps


def opt_arg_wrap(inner_wrap):
    def wrapped_dec(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return inner_wrap(args[0])
        else:
            def wrap_with_arg(func):
                return inner_wrap(func, *args, **kwargs)
            return wrap_with_arg
    return wrapped_dec
