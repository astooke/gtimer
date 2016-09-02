
"""
Timer() functions acting on global variables (most exposed to user).
"""

from timeit import default_timer as timer

from gtimer.private import glob as g
from gtimer.private import times as times_glob


__all__ = ['start', 'stamp', 'stop', 'pause', 'resume', 'b_stamp']


#
# Functions to expose to user.
#


def start():
    if g.sf.cum:
        raise RuntimeError("Already have stamps, can't start again (must reset).")
    if g.tf.subdvsn_awaiting or g.rf.subdvsn or g.tf.par_subdvsn_awaiting or g.rf.subdvsn:
        raise RuntimeError("Already have lower level timers, can't start again (must reset).")
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped (must open new or reset).")
    g.tf.paused = False
    g.tf.tmp_total = 0.  # (In case previously paused.)
    t = timer()
    g.tf.start_t = t
    g.tf.last_t = t
    return t


def stamp(name, unique=True, keep_subdivisions=True):
    t = timer()
    elapsed = t - g.tf.last_t
    name = str(name)
    unique = bool(unique)
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    if g.tf.in_loop:
        _loop_stamp(name, elapsed, unique)
    else:
        if name not in g.sf.cum:
            g.sf.cum[name] = elapsed
            g.sf.order.append(name)
        elif unique:
            raise ValueError("Duplicate stamp name: {}".format(name))
        else:
            g.sf.cum[name] += elapsed
    times_glob.assign_subdivisions(name, keep_subdivisions)
    g.tf.last_t = timer()
    g.tf.self_cut += g.tf.last_t - t
    return t


def stop(name=None, unique=True, keep_subdivisions=True):
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if name is not None:
        if g.tf.paused:
            raise RuntimeError("Cannot apply stopping stamp to paused timer.")
        stamp(name, unique, keep_subdivisions)
    else:
        times_glob.assign_subdivisions(g.UNASGN, keep_subdivisions)
    for s in g.tf.rgstr_stamps:
        if s not in g.sf.cum:
            g.sf.cum[s] = 0.
            g.sf.order.append(s)
    if not g.tf.paused:
        g.tf.tmp_total += t - g.tf.start_t
    g.tf.tmp_total -= g.tf.self_cut
    g.tf.self_cut += timer() - t  # AFTER subtraction from tmp_total, before dump
    times_glob.dump_times()
    g.tf.stopped = True
    return t


def pause():
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer already paused.")
    g.tf.paused = True
    g.tf.tmp_total += t - g.tf.start_t
    g.tf.start_t = None
    g.tf.last_t = None
    return t


def resume():
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if not g.tf.paused:
        raise RuntimeError("Timer was not paused.")
    g.tf.paused = False
    g.tf.start_t = t
    g.tf.last_t = t
    return t


def b_stamp(name=None, unique=False, keep_subdivisions=False):
    """Blank stamp (same signature as stamp())."""
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    times_glob.assign_subdivisions(g.UNASGN, keep_subdivisions)
    g.tf.last_t = timer()
    g.tf.self_cut += g.tf.last_t - t
    return t


#
# Private helper functions.
#


def _loop_stamp(name, elapsed, unique=True):
    if name not in g.lf.stamps:  # (first time this loop gets this name)
        _init_loop_stamp(name, unique)
    if g.lf.itr_stamp_used[name]:
        if unique:
            raise ValueError("Loop stamp name twice in one itr: {}".format(name))
    else:
        g.lf.itr_stamp_used[name] = True
    g.lf.itr_stamps[name] += elapsed


def _init_loop_stamp(name, unique=True, do_lf=True):
    if unique and name in g.sf.cum:
        raise ValueError("Duplicate stamp name (in or at loop): {}".format(name))
    if do_lf:
        g.lf.stamps.append(name)
        g.lf.itr_stamp_used[name] = False
        g.lf.itr_stamps[name] = 0.
        if g.lf.save_itrs:
            g.sf.itrs[name] = []
    g.sf.cum[name] = 0.
    g.sf.itr_num[name] = 0
    g.sf.itr_max[name] = 0.
    g.sf.itr_min[name] = float('Inf')
    g.sf.order.append(name)
