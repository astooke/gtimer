
"""
Helper functions (not exposed to user) to be used across package (including disabled mode).
"""

import sys


def opt_arg_wrap(inner_wrap):
    def wrapped_dec(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return inner_wrap(args[0])
        else:
            def gtimer_wrapped_arg(func):
                return inner_wrap(func, *args, **kwargs)
            return gtimer_wrapped_arg
    return wrapped_dec


def compat_py2_py3():
    """ For Python 2, 3 compatibility. """
    if (sys.version_info > (3, 0)):
        def iteritems(dictionary):
            return dictionary.items()

        def itervalues(dictionary):
            return dictionary.values()

    else:
        def iteritems(dictionary):
            return dictionary.iteritems()

        def itervalues(dictionary):
            return dictionary.itervalues()

    return iteritems, itervalues


iteritems, itervalues = compat_py2_py3()
