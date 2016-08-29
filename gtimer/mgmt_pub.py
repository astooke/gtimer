
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


def subdivide(name, rgstr_stamps=list(), save_itrs=True):
    name = str(name)
    rgstr_stamps = mgmt_priv.sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.tf.subdivisions_awaiting:
        # Previous dump exists.
        # (e.g. multiple calls of same wrapped function between stamps)
        dump = g.tf.subdivisions_awaiting[name]
        g.create_next_timer(name, rgstr_stamps, save_itrs, dump)
    else:
        # No previous, write times directly to awaiting sub in parent times.
        g.create_next_timer(name, rgstr_stamps, save_itrs, parent=g.rf)
        new_times = g.rf
        g.focus_backward_timer()
        g.tf.subdivisions_awaiting[name] = new_times
        g.focus_forward_timer()
    g.tf.user_subdivision = True


def end_subdivision():
    if not g.tf.user_subdivision:
        raise RuntimeError('Attempted to end a subdivision not started by user.')
    if g.tf.in_loop:
        raise RuntimeError('Cannot close a timer while it is in timed loop.')
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


def wrap(func, subdivision=True, rgstr_stamps=list(), save_itrs=True):
    subdivision = bool(subdivision)

    if subdivision:
        name = func.__name__
        rgstr_stamps = mgmt_priv.sanitize_rgstr_stamps(rgstr_stamps)
        save_itrs = bool(save_itrs)

        def timer_wrapped(*args, **kwargs):
            mgmt_priv.subdivide(name, rgstr_stamps, save_itrs)
            result = func(*args, **kwargs)
            mgmt_priv.end_subdivision()
            return result
    else:
        def timer_wrapped(*args, **kwargs):
            return func(*args, **kwargs)

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


def attach_par_subdivisions(par_name, par_times, stamps_as_itrs=True):
    """ Manual assignment of a group of (stopped) times objects as a parallel
    subdivision of a running timer.
    """
    if not isinstance(par_times, (list, tuple)):
        raise TypeError("Expected list or tuple for par_times arg.")
    for times in par_times:
        if not isinstance(times, Times):
            raise TypeError("Expected each element of par_times to be Times object.")
        if not times.total > 0.:
            raise RuntimeError("Attached par subdivision has total time 0, either empty or not yet stopped.")
    par_name = str(par_name)
    sub_with_max_tot = max(par_times, key=lambda x: x.total)
    g.rf.self_agg += sub_with_max_tot.self_agg
    if par_name not in g.tf.par_subdivisions_awaiting:
        g.tf.par_subdivisions_awaiting[par_name] = []
        for times in par_times:
            times_copy = copy.deepcopy(times)
            times_copy.parent = g.rf
            times_copy.par_in_parent = True
            g.tf.par_subdivisions_awaiting[par_name].append(times_copy)
    else:
        for new_sub in par_times:
            is_prev_sub = False
            for old_sub in g.tf.par_subdivisions_awaiting[par_name]:
                if old_sub.name == new_sub.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                times_loc.merge_times(old_sub, new_sub, stamps_as_itrs)
            else:
                new_sub_copy = copy.deepcopy(new_sub)
                new_sub_copy.parent = g.rf
                new_sub_copy.par_in_parent = True
                g.tf.par_subdivisions_awaiting[par_name].append(new_sub_copy)


def attach_subdivision(times, stamps_as_itrs=True):
    """ Manual assignment of a (stopped) times object as a subdivision of
    running timer.
    """
    if not isinstance(times, Times):
        raise TypeError("Expected Times object input.")
    if not times.total > 0.:
        raise RuntimeError("Attached subdivision has total time 0, either empty or not yet stopped.")
    name = times.name
    g.rf.self_agg += times.self_agg
    if name not in g.tf.subdivisions_awaiting:
        times_copy = copy.deepcopy(times)
        times_copy.parent = g.rf
        g.tf.subdivisions_awaiting[name] = times_copy
    else:
        times_loc.merge_times(g.tf.subdivisions_awaiting[name],
                              times,
                              stamps_as_itrs)
