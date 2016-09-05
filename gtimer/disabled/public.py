
"""
All public functions but with no timing, so gtimer commands can be left in
place in code but timing turned off.
"""

from gtimer.disabled.private import UntimedLoop as _UntimedLoop
from gtimer.disabled.private import UntimedFor as _UntimedFor
from gtimer.util import opt_arg_wrap as _opt_arg_wrap

#
# timer
#


def start():
    pass  # Will return None instead of a time.


def stamp(*args, **kwargs):
    pass


def stop(*args, **kwargs):
    pass


def pause():
    pass


def resume():
    pass


def b_stamp(*args, **kwargs):
    pass


#
# loop
#


def timed_loop(*args, **kwargs):
    return _UntimedLoop()


def timed_for(iterable, *args, **kwargs):
    return _UntimedFor(iterable)


#
# mgmt
#


def subdivide(*args, **kwargs):
    pass


def end_subdivision(*args, **kwargs):
    pass


@_opt_arg_wrap
def wrap(func, *args, **kwargs):
    def dis_gtimer_wrapped(*arg, **kwarg):
        return func(*arg, **kwarg)
    return dis_gtimer_wrapped


def rename_root_timer(*args, **kwargs):
    pass


def set_root_save_itrs(*args, **kwargs):
    pass


def reset_current_timer():
    pass


def hard_reset():
    pass


def get_times():
    pass


def attach_par_subdivisions(*args, **kwargs):
    pass


def attach_subdivision(*args, **kwargs):
    pass


#
# report
#


def report(*args, **kwargs):
    pass


def compare(*args, **kwargs):
    pass


def write_structure(*args, **kwargs):
    pass


#
# file_io
#


def save_pkl(*args, **kwargs):
    pass


def load_pkl(*args, **kwargs):
    pass


def open_mmap(*args, **kwargs):
    pass


def close_mmap(*args, **kwargs):
    pass


def save_mmap(*args, **kwags):
    pass


def load_mmap(*args, **kwargs):
    pass
