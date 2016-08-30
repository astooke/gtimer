
"""
All public functions but with no timing, so gtimer commands can be left in
place in code but timing turned off.
"""

from disabled_priv import UntimedLoop, UntimedFor


#
# timer_glob
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
    return UntimedLoop()


def timed_for(iterable, *args, **kwargs):
    return UntimedFor(iterable)


#
# mgmt_pub
#


def subdivide(*args, **kwargs):
    pass


def end_subdivision(*args, **kwargs):
    pass


def wrap(func, *args, **kwargs):
    def untimer_wrapped():
        return func(*args, **kwargs)
    return untimer_wrapped


def rename_root_timer(*args, **kwargs):
    pass


def reset_current_timer():
    pass


def get_times():
    pass


def attach_par_subdivisions(*args, **kwargs):
    pass


def attach_subdivision(*args, **kwargs):
    pass


#
# report_glob
#


def report(*args, **kwargs):
    pass


def compare(*args, **kwargs):
    pass


def write_structure(*args, **kwargs):
    pass
