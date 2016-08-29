
"""
Timer() functions acting on global variables (most exposed to user).
"""

from timeit import default_timer as timer
import data_glob as g
import times_glob

#
# Functions to expose to user.
#


def start():
    if g.sf.cum:
        raise RuntimeError("Already have stamps, can't start again.")
    if g.tf.subdivisions_awaiting:
        raise RuntimeError("Already have lower level timers, can't start again.")
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped (must close and open new).")
    t = timer()
    g.tf.paused = False
    g.rf.total = 0.  # (In case previously paused.)
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
    if keep_subdivisions:
        if g.tf.subdivisions_awaiting:
            times_glob.assign_subdivisions(name)
        if g.tf.par_subdivisions_awaiting:
            times_glob.assign_par_subdivisions(name)
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
    if keep_subdivisions:
        if g.tf.subdivisions_awaiting:
            times_glob.assign_subdivisions(g.UNASGN)
        if g.tf.par_subdivisions_awaiting:
            times_glob.assign_par_subdivisions(g.UNASGN)
    for _, v in g.sf.cum.iteritems():
        g.sf.sum_t += v
    for s in g.tf.rgstr_stamps:
        if s not in g.sf.cum:
            g.sf.cum[s] = 0.
            g.sf.order.append(s)
    if not g.tf.paused:
        g.tf.tmp_total += t - g.tf.start_t
    stop_time = timer() - t
    g.tf.self_cut += stop_time
    g.tf.tmp_total += stop_time  # (self_cut will be subtracted)
    times_glob.dump_times()
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
    if keep_subdivisions:
        if g.tf.subdivisions_awaiting:
            times_glob.assign_subdivisions(g.UNASGN)
        if g.tf.par_subdivisions_awaiting:
            times_glob.assign_par_subdivisions(g.UNASGN)
    g.tf.last_t = timer()
    g.tf.self_cut += g.tf.last_t - t
    return t

#
# Private helper functions.
#


def _loop_stamp(name, elapsed, unique=True):
    if name not in g.lf.stamps:  # (first time this loop gets this name)
        if unique and name in g.sf.cum:
            raise ValueError("Duplicate stamp name (in loop): {}".format(name))
        g.lf.stamps.append(name)
        g.lf.itr_stamp_used[name] = False
        g.sf.cum[name] = 0.
        if g.lf.save_itrs:
            g.sf.itrs[name] = []
        g.sf.order.append(name)
    if g.lf.itr_stamp_used[name]:
        if unique:
            raise ValueError("Loop stamp name twice in one itr: {}".format(name))
        elif g.lf.save_itrs:
                g.sf.itrs[name][-1] += elapsed
    elif g.lf.save_itrs:
        g.sf.itrs[name].append(elapsed)
    g.sf.cum[name] += elapsed
    g.lf.itr_stamp_used[name] = True
