
"""
Functions for creating new timers, closing old ones, and handling the
relationships of the timers. (All exposed to user.)
"""

import data_glob as g
import timer_glob
import mgmt_priv
import copy


def open_next_timer(name, rgstr_stamps=list(), save_itrs=True):
    name = str(name)
    rgstr_stamps = mgmt_priv.sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.tf.children_awaiting:
        # Previous dump exists.
        # (e.g. multiple calls of same wrapped function between stamps)
        dump = g.tf.children_awaiting[name]
        g.create_next_timer(name, rgstr_stamps, save_itrs, dump)
    else:
        # No previous, write times directly to awaiting child in parent times.
        g.create_next_timer(name, rgstr_stamps, save_itrs, parent=g.rf)
        new_times = g.rf
        g.focus_backward_timer()
        g.tf.children_awaiting[name] = new_times
        g.focus_forward_timer()


def close_last_timer():
    if g.tf is g.root_timer:
        raise RuntimeError('Attempted to close root timer, can only stop or reset it.')
    if g.tf.in_loop:
        raise RuntimeError('Cannot close a timer while it is in timed loop.')
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


def wrap(func, rgstr_stamps=list(), save_itrs=True):
    name = func.__name__
    rgstr_stamps = mgmt_priv.sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)

    def timer_wrapped(*args, **kwargs):
        open_next_timer(name, rgstr_stamps, save_itrs)
        result = func(*args, **kwargs)
        close_last_timer()
        return result
    return timer_wrapped


def rename_root_timer(name):
    g.focus_root_timer()
    g.tf.name = str(name)
    g.focus_last_timer()


def reset_current_timer():
    """ If timer not previously stopped, times data dump will not happen, but
    relationship to parent timer remains intact.
    """
    if g.tf.in_loop:
        raise RuntimeError("Cannot reset a timer while it is in timed loop.")
    g.tf.reset()


def get_times():
    """ Returns an immediate deep copy of current Times, no risk of
    interference with active objects.
    """
    return copy.deepcopy(g.rf)
