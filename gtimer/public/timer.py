
"""
Core timer functionality provided to user.
"""

from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.private import times as times_priv
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.util import opt_arg_wrap
from gtimer.private.cont import UNASGN
from gtimer.local.exceptions import (StartError, StoppedError, PausedError,
                                     LoopError, GTimerError, UniqueNameError)


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


#
# Core timer functions.
#


def start():
    """Summary
    
    Returns:
        TYPE: Description
    
    Raises:
        RuntimeError: Description
    """
    if f.s.cum:
        raise StartError("Already have stamps, can't start again (must reset).")
    if f.t.subdvsn_awaiting or f.t.par_subdvsn_awaiting:
        raise StartError("Already have subdivisions, can't start again (must reset).")
    if f.t.stopped:
        raise StartError("Timer already stopped (must open new or reset).")
    f.t.paused = False
    f.t.tmp_total = 0.  # (In case previously paused.)
    t = timer()
    f.t.start_t = t
    f.t.last_t = t
    return t


def stamp(name, unique=None, keep_subdivisions=None, quick_print=None,
          un=None, ks=None, qp=None):
    t = timer()
    elapsed = t - f.t.last_t
    if f.t.stopped:
        raise StoppedError("Cannot stamp stopped timer.")
    if f.t.paused:
        raise PausedError("Cannot stamp paused timer.")
    name = str(name)
    # Logic: default unless either arg used.  if both args used, 'or' them.
    unique = SET['UN'] if (unique is None and un is None) else bool(unique or un)  # bool(None) becomes False
    keep_subdivisions = SET['KS'] if (keep_subdivisions is None and ks is None) else bool(keep_subdivisions or ks)
    quick_print = SET['QP'] if (quick_print is None and qp is None) else bool(quick_print or qp)
    if quick_print:
        print("({}) {}: {}".format(f.t.name, name, elapsed))
    if f.t.in_loop:
        _loop_stamp(name, elapsed, unique)
    else:
        if name not in f.s.cum:
            f.s.cum[name] = elapsed
            f.s.order.append(name)
        elif unique:
            raise UniqueNameError("Duplicate stamp name: {}".format(name))
        else:
            f.s.cum[name] += elapsed
    times_priv.assign_subdivisions(name, keep_subdivisions)
    f.t.last_t = timer()
    f.t.self_cut += f.t.last_t - t
    return t


def stop(name=None, unique=None, keep_subdivisions=None, quick_print=None,
         un=None, ks=None, qp=None):
    t = timer()
    if f.t.stopped:
        raise StoppedError("Timer already stopped.")
    unique = SET['UN'] if (unique is None and un is None) else bool(unique or un)  # bool(None) becomes False
    keep_subdivisions = SET['KS'] if (keep_subdivisions is None and ks is None) else bool(keep_subdivisions or ks)
    quick_print = SET['QP'] if (quick_print is None and qp is None) else bool(quick_print or qp)
    if name is not None:
        if f.t.paused:
            raise PausedError("Cannot apply stopping stamp to paused timer.")
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
        raise StoppedError("Cannot pause stopped timer.")
    if f.t.paused:
        raise PausedError("Timer already paused.")
    f.t.paused = True
    f.t.tmp_total += t - f.t.start_t
    f.t.start_t = None
    f.t.last_t = None
    return t


def resume():
    t = timer()
    if f.t.stopped:
        raise StoppedError("Cannot resume stopped timer.")
    if not f.t.paused:
        raise PausedError("Cannot resume timer that is not paused.")
    f.t.paused = False
    f.t.start_t = t
    f.t.last_t = t
    return t


def b_stamp(name=None, unique=None, keep_subdivisions=False, quick_print=None,
            un=None, ks=False, qp=None):
    """Blank stamp (same signature as stamp())."""
    t = timer()
    if f.t.stopped:
        raise StoppedError("Cannot b_stamp stopped timer.")
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
        raise LoopError("Cannot reset a timer while it is in timed loop.")
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
            save_itrs = SET['SI'] if wrap_save_itrs is None else wrap_save_itrs
            _auto_subdivide(name, rgstr_stamps, save_itrs=save_itrs)
            result = func(*args, **kwargs)
            _end_auto_subdivision()
            return result
    else:
        def gtimer_wrapped(*args, **kwargs):
            return func(*args, **kwargs)

    return gtimer_wrapped


def subdivide(name, rgstr_stamps=None, save_itrs=SET['SI']):
    _auto_subdivide(name, rgstr_stamps, save_itrs)
    f.t.is_user_subdvsn = True


def end_subdivision():
    if not f.t.is_user_subdvsn:
        raise GTimerError('Attempted to end a subdivision not started by user.')
    if f.t.in_loop:
        raise LoopError('Cannot close a timer while it is in timed loop.')
    _close_subdivision()


#
# Functions operating on the root timer.
#


def rename_root(name):
    f.root.name = str(name)
    f.root.times.name = str(name)


def set_save_itrs_root(setting):
    f.root.times.save_itrs = bool(setting)


def rgstr_stamps_root(rgstr_stamps):
    f.root.rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)


def reset_root():
    f.hard_reset()


#
# Timer status queries.
#


def is_timer_stopped():
    return f.t.stopped


def is_timer_paused():
    return f.t.paused


def has_subdvsn_awaiting():
    return bool(f.t.subvsn_awaiting)


def has_par_subdvsn_awaiting():
    return bool(f.t.par_subdvsn_awaiting)


def get_active_lineage():
    lin_str = ''
    for active_timer in f.timer_stack:
        lin_str += "{}-->".format(active_timer.name)
    try:
        return lin_str[:-3]
    except IndexError:
        pass


#
# Functions adjusting the (global) default settings.
#


def set_def_save_itrs(setting):
    SET['SI'] = bool(setting)


def set_def_keep_subdivisions(setting):
    SET['KS'] = bool(setting)


def set_def_quick_print(setting):
    SET['QP'] = bool(setting)


def set_def_unique(setting):
    SET['UN'] = bool(setting)


#
# Drop awaiting subdivisions.
#


def clear_subdvsn_awaiting():
    f.t.subdvsn_awaiting.clear()


def clear_par_subdvsn_awaiting():
    f.t.par_subdvsn_awaiting.clear()


#
# Private helper functions.
#


def _loop_stamp(name, elapsed, unique=True):
    if name not in f.lp.stamps:  # (first time this loop gets this name)
        _init_loop_stamp(name, unique)
    if f.lp.itr_stamp_used[name]:
        if unique:
            raise UniqueNameError("Loop stamp name twice in one itr: {}".format(name))
    else:
        f.lp.itr_stamp_used[name] = True
    f.lp.itr_stamps[name] += elapsed


def _init_loop_stamp(name, unique=True, do_lp=True):
    if unique and name in f.s.cum:
        raise UniqueNameError("Duplicate stamp name (in or at loop): {}".format(name))
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
        raise GTimerError("gtimer attempted to end user-generated subdivision.")
    assert not f.t.in_loop, "gtimer attempted to close subidivision while in timed loop."
    _close_subdivision()
