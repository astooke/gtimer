
"""
Functions for creating new timers, closing old ones, and handling the
relationships of the timers. (All exposed to user.)
"""

from timeit import default_timer as timer
import copy

from gtimer.private import glob as g
from gtimer.public import timer as timer_glob
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.local.times import Times
from gtimer.local import merge

__all__ = ['subdivide',
           'end_subdivision',
           'wrap',
           'rename_root_timer',
           'set_root_save_itrs',
           'reset_current_timer',
           'get_times',
           'attach_par_subdivision',
           'attach_subdivision',
           ]


def subdivide(name, rgstr_stamps=list(), save_itrs=True):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.tf.subdvsn_awaiting:
        # Previous dump exists.
        # (e.g. multiple calls of same wrapped function between stamps)
        dump = g.tf.subdvsn_awaiting[name]
        g.create_next_timer(name, rgstr_stamps, dump, save_itrs=save_itrs)
    else:
        # No previous, write times directly to awaiting sub in parent times.
        g.create_next_timer(name, rgstr_stamps, save_itrs=save_itrs, parent=g.rf)
        g.tfmin1.subdvsn_awaiting[name] = g.rf
    g.tf.user_subdivision = True


def end_subdivision():
    if not g.tf.user_subdivision:
        raise RuntimeError('Attempted to end a subdivision not started by user.')
    if g.tf.in_loop:
        raise RuntimeError('Cannot close a timer while it is in timed loop.')
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


#
# A few private helper functions.
#


def _auto_subdivide(*args, **kwargs):
    """ To be called internally instead of public version."""
    subdivide(*args, **kwargs)
    g.tf.user_subdivision = False  # Protect from user closure.


def _end_auto_subdivision():
    """ To be called internally instead of public version."""
    if g.tf.user_subdivision:
        raise RuntimeError("gtimer attempted to end user-generated subdivision.")
    assert not g.tf.in_loop, "gtimer attempted to close subidivision while in timed loop."
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


def _opt_arg_wrap(inner_wrap):
    def wrapped_dec(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return inner_wrap(args[0])
        else:
            def wrap_with_arg(func):
                return inner_wrap(func, *args, **kwargs)
            return wrap_with_arg
    return wrapped_dec


#
# Back to public.
#


@_opt_arg_wrap
def wrap(func, subdivision=True, rgstr_stamps=list(), save_itrs=True):
    subdivision = bool(subdivision)
    if subdivision:
        name = func.__name__
        rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
        save_itrs = bool(save_itrs)

        def timer_wrapped(*args, **kwargs):
            _auto_subdivide(name, rgstr_stamps, save_itrs=save_itrs)
            result = func(*args, **kwargs)
            _end_auto_subdivision()
            return result
    else:
        def timer_wrapped(*args, **kwargs):
            return func(*args, **kwargs)

    return timer_wrapped


def rename_root_timer(name):
    g.root_timer.name = str(name)
    g.root_timer.times.name = str(name)


def set_root_save_itrs(setting=True):
    g.root_timer.times.save_itrs = bool(setting)


def reset_current_timer():
    """ If timer not previously stopped, times data dump will not happen.
    Relationship to parent timer remains intact.
    """
    if g.tf.in_loop:
        raise RuntimeError("Cannot reset a timer while it is in timed loop.")
    g.tf.reset()
    g.refresh_shortcuts()


def get_times():
    """ Returns an immediate deep copy of current Times, no risk of
    interference with active objects.
    """
    if g.root_timer.stopped:
        return copy.deepcopy(g.root_timer.times)
    else:
        t = timer()
        times = mgmt_priv.collapse_times()
        g.root_timer.self_cut += timer() - t
        return times


def attach_par_subdivision(par_name, par_times):
    """ Manual assignment of a group of (stopped) times objects as a parallel
    subdivision of a running timer.
    """
    t = timer()
    if not isinstance(par_times, (list, tuple)):
        raise TypeError("Expected list or tuple for par_times arg.")
    for times in par_times:
        if not isinstance(times, Times):
            raise TypeError("Expected each element of par_times to be Times object.")
        assert times.total > 0., "An attached par subdivision has total time 0, appears empty."
    par_name = str(par_name)
    sub_with_max_tot = max(par_times, key=lambda x: x.total)
    g.rf.self_agg += sub_with_max_tot.self_agg
    if par_name not in g.tf.par_subdvsn_awaiting:
        g.tf.par_subdvsn_awaiting[par_name] = []
        for times in par_times:
            times_copy = copy.deepcopy(times)
            times_copy.parent = g.rf
            times_copy.par_in_parent = True
            g.tf.par_subdvsn_awaiting[par_name].append(times_copy)
    else:
        for new_sub in par_times:
            is_prev_sub = False
            for old_sub in g.tf.par_subdvsn_awaiting[par_name]:
                if old_sub.name == new_sub.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                merge.merge_times(old_sub, new_sub)
            else:
                new_sub_copy = copy.deepcopy(new_sub)
                new_sub_copy.parent = g.rf
                new_sub_copy.par_in_parent = True
                g.tf.par_subdvsn_awaiting[par_name].append(new_sub_copy)
    g.tf.self_cut += timer() - t


def attach_subdivision(times):
    """ Manual assignment of a (stopped) times object as a subdivision of
    running timer.
    """
    t = timer()
    if not isinstance(times, Times):
        raise TypeError("Expected Times object input.")
    assert times.total > 0., "Attached subdivision has total time 0, appears empty."
    name = times.name
    g.rf.self_agg += times.self_agg
    if name not in g.tf.subdvsn_awaiting:
        times_copy = copy.deepcopy(times)
        times_copy.parent = g.rf
        g.tf.subdvsn_awaiting[name] = times_copy
    else:
        merge.merge_times(g.tf.subdvsn_awaiting[name], times)
    g.tf.self_cut += timer() - t
