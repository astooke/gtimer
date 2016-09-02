
"""
Timer management functions to hide from user but expose
elsewhere in package.
"""

from timeit import default_timer as timer

from gtimer.private import glob as g
from gtimer.private import times as times_glob
from gtimer.public import timer as timer_glob
from gtimer.local.util import sanitize_rgstr_stamps


def auto_subdivide(name, rgstr_stamps=list(), save_itrs=True):
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


def subdivide_named_loop(name, rgstr_stamps, save_itrs):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.rf.subdvsn:
        assert len(g.rf.subdvsn[name]) == 1
        dump = g.rf.subdvsn[name][0]
        g.create_next_timer(name,
                            rgstr_stamps,
                            named_loop=True,
                            in_loop=True,
                            save_itrs=save_itrs)
        g.tf.dump = dump
    else:
        # No previous, write directly to assigned subdivision in parent times.
        g.create_next_timer(name,
                            rgstr_stamps,
                            named_loop=True,
                            in_loop=True,
                            parent=g.rf,
                            pos_in_parent=name,
                            save_itrs=save_itrs)
        g.rfmin1.subdvsn[name] = [g.rf]


def end_auto_subdivision():
    """ To be called internally instead of public version."""
    if g.tf.user_subdivision:
        raise RuntimeError("gtimer attempted to end user-generated subdivision.")
    assert not g.tf.in_loop, "gtimer attempted to close subidivision while in timed loop."
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


#
# Loops.
#

def enter_loop(name=None,
               rgstr_stamps=list(),
               save_itrs=True,
               keep_subdivisions=True):
    t = timer()
    g.tf.last_t = t
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    times_glob.assign_subdivisions(g.UNASGN, keep_subdivisions)
    if name is None:  # Entering anonynous loop.
        if g.tf.in_loop:
            raise RuntimeError("Entering anonymous inner timed loop (not supported).")
        g.tf.in_loop = True
        g.tf.self_cut += timer() - t
    else:  # Entering a named loop.
        if not g.tf.in_loop or name not in g.lf.stamps:  # double check this if-logic
            timer_glob._init_loop_stamp(name, do_lf=False)
            if save_itrs:
                g.sf.itrs[name] = []
        if g.tf.in_loop and name not in g.lf.stamps:
            g.lf.stamps.append(name)
        g.tf.self_cut += timer() - t
        subdivide_named_loop(name, rgstr_stamps, save_itrs=save_itrs)
    g.create_next_loop(name, rgstr_stamps, save_itrs)


def loop_start():
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    for k in g.lf.itr_stamps:
        # (these are initialized together with same key)
        g.lf.itr_stamps[k] = 0.
        g.lf.itr_stamp_used[k] = False


def loop_end(loop_end_stamp=None,
             end_stamp_unique=True,
             keep_subdivisions=True):
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if loop_end_stamp is not None:
        timer_glob.stamp(loop_end_stamp,
                         end_stamp_unique,
                         keep_subdivisions)
        t = timer()
    else:
        t = timer()
        g.tf.last_t = t
        times_glob.assign_subdivisions(g.UNASGN, keep_subdivisions)

    # Prevserve the ordering of stamp names as much as possible, wait until
    # after first pass to initialize any unused registered stamps.
    if g.lf.first_itr:
        g.lf.first_itr = False
        for s in g.lf.rgstr_stamps:
            if s not in g.lf.stamps:
                timer_glob._init_loop_stamp(s)
    for s, used in g.lf.itr_stamp_used.iteritems():
        if used:
            val = g.lf.itr_stamps[s]
            g.sf.cum[s] += val
            if g.lf.save_itrs:
                g.sf.itrs[s].append(val)
            else:
                g.sf.itr_num[s] += 1
                if val > g.sf.itr_max[s]:
                    g.sf.itr_max[s] = val
                if val < g.sf.itr_min[s]:
                    g.sf.itr_min[s] = val
        elif g.lf.save_itrs and s in g.lf.rgstr_stamps:
            g.sf.itrs[s].append(0.)
    if g.lf.name is not None:
        # Reach back and stamp in the parent timer.
        elapsed = t - g.tfmin1.last_t
        g.sfmin1.cum[g.lf.name] += elapsed
        if g.lf.save_itrs:
            g.sfmin1.itrs[g.lf.name].append(elapsed)
        else:
            g.sfmin1.itr_num[g.lf.name] += 1
            if elapsed > g.sfmin1.itr_max[g.lf.name]:
                g.sfmin1.itr_max[g.lf.name] = elapsed
            if elapsed < g.sfmin1.itr_min[g.lf.name]:
                g.sfmin1.itr_min[g.lf.name] = elapsed
        g.tfmin1.last_t = t
    g.tf.self_cut += timer() - t


def exit_loop():
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused at loop exit (uncertain behavior--not allowed).")
    g.tf.in_loop = False
    if g.lf.name is not None:
        end_auto_subdivision()
    g.remove_last_loop()
