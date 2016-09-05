
"""
Helper functions (not exposed to user) to be used across package (including disabled mode).
"""


def opt_arg_wrap(inner_wrap):
    def wrapped_dec(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return inner_wrap(args[0])
        else:
            def gtimer_wrapped_arg(func):
                return inner_wrap(func, *args, **kwargs)
            return gtimer_wrapped_arg
    return wrapped_dec
