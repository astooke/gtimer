
"""
Functions for creating new timers, closing old ones, and handling the
relationships of the timers. (All exposed to user.)
"""

import data_glob as g
import timer_glob
import mgmt_priv
import copy
from timer_classes import Times
import times_loc


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
    g.root_timer.name = str(name)


def reset_current_timer():
    """ If timer not previously stopped, times data dump will not happen.
    Relationship to parent timer remains intact.
    """
    if g.tf.in_loop:
        raise RuntimeError("Cannot reset a timer while it is in timed loop.")
    g.tf.reset()


def get_times():
    """ Returns an immediate deep copy of current Times, no risk of
    interference with active objects.
    """
    return copy.deepcopy(g.rf)


def attach_par_children(name, par_times):
    if not isinstance(par_times, (list, tuple)):
        raise TypeError("Expected list or tuple for par_times arg.")
    for times in par_times:
        if not isinstance(times, Times):
            raise TypeError("Expected each element of par_times to be Times object.")
    name = str(name)
    if name not in g.tf.par_children_awaiting:
        g.tf.par_children_awaiting[name] = []
    times_list_copy = []
    for times in par_times:
        times_list_copy.append(copy.deepcopy(par_times))
    for times in times_list_copy:
        times.parent = g.rf
        times.par_in_parent = True
    g.tf.par_children_awaiting[name] += times_list_copy


def attach_child(times, stamps_as_itrs=True):
    if not isinstance(times, Times):
        raise TypeError("Expected Times object input.")
    times_copy = copy.deepcopy(times)
    name = times_copy.name
    if name not in g.tf.children_awaiting:
        g.tf.children_awaiting[name] = times_copy
    else:
        dump = g.tf.children_awaiting[name]
        times_loc.merge_times(dump, times, stamps_as_itrs)
