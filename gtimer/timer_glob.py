
"""
Timer() functions acting on global variables (many exposed to user).
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
    if g.tf.children_awaiting:
        raise RuntimeError("Already have lower level timers, can't start again.")
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped (must close and open new).")
    t = timer()
    g.tf.paused = False
    g.rf.total = 0.  # (In case previously paused.)
    g.tf.start_t = t
    g.tf.last_t = t
    return t


def stamp(name, unique=True):
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
    if g.tf.children_awaiting:
        times_glob.l_assign_children(name)
    g.tf.last_t = t
    g.rf.self_cut += timer() - t
    g.rf.self_agg += g.rf.self_cut
    return t


def stop(name=None, unique=True):
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if name is not None:
        if g.tf.paused:
            raise RuntimeError("Cannot apply stopping stamp to paused timer.")
        stamp(name, unique)
    else:
        if g.tf.children_awaiting:
            times_glob.l_assign_children(g.UNASGN)
    for _, v in g.sf.cum.iteritems():
        g.sf.sum_t += v
    for s in g.tf.rgstr_stamps:
        if s not in g.sf.cum:
            g.sf.cum[s] = 0.
            g.sf.order.append(s)
    if not g.tf.pause:
        g.tf.tmp_total += t - g.tf.start_t
    g.rf.total = g.tf.tmp_total - g.rf.self_cut
    g.rf.self_cut += timer() - t  # (Add after setting g.rf.total)
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


def b_stamp(*args, **kwargs):
    """Blank stamp."""
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    t = timer()
    g.tf.last_t = t
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
                g.sf.itrs[name] += elapsed
    elif g.lf.save_itrs:
        g.sf.itrs[name].append(elapsed)
    g.sf.cum[name] += elapsed
    g.lf.itr_stamp_used[name] = True
