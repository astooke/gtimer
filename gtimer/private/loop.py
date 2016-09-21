
"""
Internal functionality for timed loops.
"""
from __future__ import absolute_import, print_function
from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.private import times as times_priv
from gtimer.public import timer as timer_pub
from gtimer.util import iteritems
from gtimer.private.const import UNASGN
from gtimer.local.exceptions import StoppedError, PausedError, LoopError


def enter_loop(name=None,
               rgstr_stamps=None,
               save_itrs=True,
               keep_subdivisions=True):
    t = timer()
    f.t.last_t = t
    if f.t.stopped:
        raise StoppedError("Timer already stopped when entering loop.")
    if f.t.paused:
        raise PausedError("Timer paused when entering loop.")
    times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    if name is None:  # Entering anonynous loop.
        if f.t.in_loop:
            raise LoopError("Entering anonymous inner timed loop (not supported).")
        f.t.in_loop = True
        f.t.self_cut += timer() - t
    else:  # Entering a named loop.
        if not f.t.in_loop or name not in f.lp.stamps:  # double check this if-logic
            timer_pub._init_loop_stamp(name, do_lp=False)
            if save_itrs:
                f.s.itrs[name] = []
        if f.t.in_loop and name not in f.lp.stamps:
            f.lp.stamps.append(name)
        f.t.self_cut += timer() - t
        _subdivide_named_loop(name, rgstr_stamps, save_itrs=save_itrs)
    f.create_next_loop(name, rgstr_stamps, save_itrs)


def loop_start():
    if f.t.stopped:
        raise StoppedError("Timer already stopped at start of loop iteration.")
    if f.t.paused:
        raise PausedError("Timer paused at start of loop iteration.")
    for k in f.lp.itr_stamps:
        # (these are initialized together with same key)
        f.lp.itr_stamps[k] = 0.
        f.lp.itr_stamp_used[k] = False


def loop_end(loop_end_stamp=None,
             end_stamp_unique=True,
             keep_subdivisions=True,
             quick_print=False):
    if f.t.stopped:
        raise StoppedError("Timer already stopped at end of loop iteration.")
    if f.t.paused:
        raise PausedError("Timer paused at end of loop iteration.")
    if loop_end_stamp is not None:
        timer_pub.stamp(loop_end_stamp,
                        un=end_stamp_unique,
                        ks=keep_subdivisions,
                        qp=quick_print)
        t = timer()
    else:
        t = timer()
        f.t.last_t = t
        times_priv.assign_subdivisions(UNASGN, keep_subdivisions)

    # Prevserve the ordering of stamp names as much as possible, wait until
    # after first pass to initialize any unused registered stamps.
    if f.lp.first_itr:
        f.lp.first_itr = False
        for s in f.lp.rgstr_stamps:
            if s not in f.lp.stamps:
                timer_pub._init_loop_stamp(s)
    for s, used in iteritems(f.lp.itr_stamp_used):
        if used:
            val = f.lp.itr_stamps[s]
            f.s.cum[s] += val
            if f.lp.save_itrs:
                f.s.itrs[s].append(val)
            else:
                f.s.itr_num[s] += 1
                if val > f.s.itr_max[s]:
                    f.s.itr_max[s] = val
                if val < f.s.itr_min[s]:
                    f.s.itr_min[s] = val
        elif f.lp.save_itrs and s in f.lp.rgstr_stamps:
            f.s.itrs[s].append(0.)
    if f.lp.name is not None:
        # Reach back and stamp in the parent timer.
        elapsed = t - f.tm1.last_t
        f.sm1.cum[f.lp.name] += elapsed
        if f.lp.save_itrs:
            f.sm1.itrs[f.lp.name].append(elapsed)
        else:
            f.sm1.itr_num[f.lp.name] += 1
            if elapsed > f.sm1.itr_max[f.lp.name]:
                f.sm1.itr_max[f.lp.name] = elapsed
            if elapsed < f.sm1.itr_min[f.lp.name]:
                f.sm1.itr_min[f.lp.name] = elapsed
        f.tm1.last_t = t
        if quick_print:
            print("({}) {}: {:.4f}".format(f.tm1.name, f.lp.name, elapsed))
    f.t.self_cut += timer() - t


def exit_loop():
    if f.t.stopped:
        raise StoppedError("Timer already stopped when exiting loop.")
    if f.t.paused:
        raise PausedError("Timer paused when exiting loop.")
    f.t.in_loop = False
    if f.lp.name is not None:
        _end_subdivision_named_loop()
    f.remove_last_loop()


#
# Private helper functions.
#


def _subdivide_named_loop(name, rgstr_stamps, save_itrs):
    name = str(name)
    save_itrs = bool(save_itrs)
    if name in f.r.subdvsn:
        assert len(f.r.subdvsn[name]) == 1
        dump = f.r.subdvsn[name][0]
        f.create_next_timer(name,
                            rgstr_stamps=rgstr_stamps,
                            is_named_loop=True,
                            in_loop=True,
                            save_itrs=save_itrs)
        f.t.dump = dump
    else:
        # No previous, write directly to assigned subdivision in parent times.
        f.create_next_timer(name,
                            rgstr_stamps=rgstr_stamps,
                            is_named_loop=True,
                            in_loop=True,
                            parent=f.r,
                            pos_in_parent=name,
                            save_itrs=save_itrs)
        f.rm1.subdvsn[name] = [f.r]


def _end_subdivision_named_loop():
    if f.t.is_user_subdvsn:
        raise LoopError("gtimer attempted to end user-generated subdivision at end of named loop.")
    if not f.t.stopped:
        timer_pub.stop()
    f.remove_last_timer()
