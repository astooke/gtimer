
"""
Core timer functionality provided to user.
"""

from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.private import times as times_priv
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.util import opt_arg_wrap
from gtimer.private.cont import UNASGN


__all__ = ['start', 'stamp', 'stop', 'pause', 'resume', 'b_stamp', 'reset',
           'rename_root', 'set_save_itrs_root', 'rgstr_stamps_root', 'reset_root',
           'set_def_save_itrs', 'set_def_keep_subdivisions', 'set_def_quick_print', 'set_def_unique']


#
# Settings.
#

SET = {'SI': True,  # save iterations
       'KS': True,  # keep subdivisions
       'QP': False,  # quick print
       'UN': True,  # unique (stamp name)
       }

# Shortcuts.
SI = SET['SI']
KS = SET['KS']
QP = SET['QP']
UN = SET['UN']


#
# Core timer functions.
#


def start():
    if f.s.cum:
        raise RuntimeError("Already have stamps, can't start again (must reset).")
    if f.t.subdvsn_awaiting or f.r.subdvsn or f.t.par_subdvsn_awaiting or f.r.subdvsn:
        raise RuntimeError("Already have lower level timers, can't start again (must reset).")
    if f.t.stopped:
        raise RuntimeError("Timer already stopped (must open new or reset).")
    f.t.paused = False
    f.t.tmp_total = 0.  # (In case previously paused.)
    t = timer()
    f.t.start_t = t
    f.t.last_t = t
    return t


def stamp(name, unique=UN, keep_subdivisions=KS, quick_print=QP,
          un=UN, ks=KS, qp=QP):
    t = timer()
    elapsed = t - f.t.last_t
    if f.t.stopped:
        raise RuntimeError("Timer already stopped.")
    if f.t.paused:
        raise RuntimeError("Timer paused.")
    name = str(name)
    # Logic: if either long-form or short-form overrides default, use (not default).
    unique = (not UN and (unique or un)) or (unique and un)
    keep_subdivisions = (not KS and (keep_subdivisions or ks) or (keep_subdivisions and ks))
    quick_print = (not QP and (quick_print or qp) or (quick_print and qp))
    if quick_print:
        print("({}) {}: {}".format(f.t.name, name, elapsed))
    if f.t.in_loop:
        _loop_stamp(name, elapsed, unique)
    else:
        if name not in f.s.cum:
            f.s.cum[name] = elapsed
            f.s.order.append(name)
        elif unique:
            raise ValueError("Duplicate stamp name: {}".format(name))
        else:
            f.s.cum[name] += elapsed
    times_priv.assign_subdivisions(name, keep_subdivisions)
    f.t.last_t = timer()
    f.t.self_cut += f.t.last_t - t
    return t


def stop(name=None, unique=UN, keep_subdivisions=KS, quick_print=QP,
         un=UN, ks=KS, qp=QP):
    t = timer()
    if f.t.stopped:
        raise RuntimeError("Timer already stopped.")
    unique = (not UN and (unique or un)) or (unique and un)
    keep_subdivisions = (not KS and (keep_subdivisions or ks) or (keep_subdivisions and ks))
    quick_print = (not QP and (quick_print or qp) or (quick_print and qp))
    if name is not None:
        if f.t.paused:
            raise RuntimeError("Cannot apply stopping stamp to paused timer.")
        stamp(name, un=unique, ks=keep_subdivisions, qp=quick_print)
    else:
        times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    for s in f.t.rgstr_stamps:
        if s not in f.s.cum:
            f.s.cum[s] = 0.
            f.s.order.append(s)
    if not f.t.paused:
        f.t.tmp_total += t - f.t.start_t
    f.t.tmp_total -= f.t.self_cut
    f.t.self_cut += timer() - t  # AFTER subtraction from tmp_total, before dump
    times_priv.dump_times()
    f.t.stopped = True
    if quick_print:
        print("({}) Total: {}".format(f.t.name, f.r.total))
    return t


def pause():
    t = timer()
    if f.t.stopped:
        raise RuntimeError("Timer already stopped.")
    if f.t.paused:
        raise RuntimeError("Timer already paused.")
    f.t.paused = True
    f.t.tmp_total += t - f.t.start_t
    f.t.start_t = None
    f.t.last_t = None
    return t


def resume():
    t = timer()
    if f.t.stopped:
        raise RuntimeError("Timer already stopped.")
    if not f.t.paused:
        raise RuntimeError("Timer was not paused.")
    f.t.paused = False
    f.t.start_t = t
    f.t.last_t = t
    return t


def b_stamp(name=None, unique=None, keep_subdivisions=False, quick_print=None,
            un=None, ks=False, qp=None):
    """Blank stamp (same signature as stamp())."""
    t = timer()
    if f.t.stopped:
        raise RuntimeError("Timer already stopped.")
    keep_subdivisions = (keep_subdivisions or ks)
    times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    f.t.last_t = timer()
    f.t.self_cut += f.t.last_t - t
    return t


def reset():
    """ If timer not previously stopped, times data dump will not happen.
    Relationship to parent timer remains intact.
    """
    if f.t.in_loop:
        raise RuntimeError("Cannot reset a timer while it is in timed loop.")
    f.t.reset()
    f.refresh_shortcuts()


#
# Timer hierarchy.
#


@opt_arg_wrap
def wrap(func, subdivide=True, name=None, rgstr_stamps=None, save_itrs=None):
    subdivision = bool(subdivide)
    if subdivision:
        name = func.__name__ if name is None else str(name)
        rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
        wrap_save_itrs = save_itrs

        def gtimer_wrapped(*args, **kwargs):
            if wrap_save_itrs is not None:
                save_itrs = wrap_save_itrs
            else:
                save_itrs = SI
            _auto_subdivide(name, rgstr_stamps, save_itrs=save_itrs)
            result = func(*args, **kwargs)
            _end_auto_subdivision()
            return result
    else:
        def gtimer_wrapped(*args, **kwargs):
            return func(*args, **kwargs)

    return gtimer_wrapped


def subdivide(name, rgstr_stamps=None, save_itrs=SI):
    _auto_subdivide(name, rgstr_stamps, save_itrs)
    f.t.is_user_subdvsn = True


def end_subdivision():
    if not f.t.is_user_subdvsn:
        raise RuntimeError('Attempted to end a subdivision not started by user.')
    if f.t.in_loop:
        raise RuntimeError('Cannot close a timer while it is in timed loop.')
    _close_subdivision()


#
# Functions operating on the root timer.
#


def rename_root(name):
    f.root.name = str(name)
    f.root.times.name = str(name)


def set_save_itrs_root(setting=True):
    f.root.times.save_itrs = bool(setting)


def rgstr_stamps_root(rgstr_stamps):
    f.root.rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)


def reset_root():
    f.hard_reset()


#
# Functions to adjust the (global) default settings.
#


def set_def_save_itrs(setting=True):
    global SET, SI
    SET['SI'] = bool(setting)
    SI = SET['SI']


def set_def_keep_subdivisions(setting=True):
    global SET, KS
    SET['KS'] = bool(setting)
    KS = SET['KS']


def set_def_quick_print(setting=True):
    global SET, QP
    SET['QP'] = bool(setting)
    QP = SET['QP']


def set_def_unique(setting=True):
    global SET, UN
    SET['UN'] = bool(setting)
    UN = SET['UN']


#
# Private helper functions.
#


def _loop_stamp(name, elapsed, unique=True):
    if name not in f.lp.stamps:  # (first time this loop gets this name)
        _init_loop_stamp(name, unique)
    if f.lp.itr_stamp_used[name]:
        if unique:
            raise ValueError("Loop stamp name twice in one itr: {}".format(name))
    else:
        f.lp.itr_stamp_used[name] = True
    f.lp.itr_stamps[name] += elapsed


def _init_loop_stamp(name, unique=True, do_lp=True):
    if unique and name in f.s.cum:
        raise ValueError("Duplicate stamp name (in or at loop): {}".format(name))
    if do_lp:
        f.lp.stamps.append(name)
        f.lp.itr_stamp_used[name] = False
        f.lp.itr_stamps[name] = 0.
        if f.lp.save_itrs:
            f.s.itrs[name] = []
    f.s.cum[name] = 0.
    f.s.itr_num[name] = 0
    f.s.itr_max[name] = 0.
    f.s.itr_min[name] = float('Inf')
    f.s.order.append(name)


def _auto_subdivide(name, rgstr_stamps=None, save_itrs=True):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in f.t.subdvsn_awaiting:
        # Previous dump exists.
        # (e.f. multiple calls of same wrapped function between stamps)
        dump = f.t.subdvsn_awaiting[name]
        f.create_next_timer(name, rgstr_stamps, dump, save_itrs=save_itrs)
    else:
        # No previous, write times directly to awaiting sub in parent times.
        f.create_next_timer(name, rgstr_stamps, save_itrs=save_itrs, parent=f.r)
        f.tm1.subdvsn_awaiting[name] = f.r


def _close_subdivision():
    if not f.t.stopped:
        stop()
    f.remove_last_timer()


def _end_auto_subdivision():
    if f.t.is_user_subdvsn:
        raise RuntimeError("gtimer attempted to end user-generated subdivision.")
    assert not f.t.in_loop, "gtimer attempted to close subidivision while in timed loop."
    _close_subdivision()
