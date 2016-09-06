
"""
Core timer functionality provided to user.
"""

from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.private import times as times_priv
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.util import opt_arg_wrap
from gtimer.private.const import UNASGN
from gtimer.local.exceptions import (StartError, StoppedError, PausedError,
                                     LoopError, GTimerError, UniqueNameError)


__all__ = ['start', 'stamp', 'stop', 'pause', 'resume', 'b_stamp', 'reset',
           'wrap', 'subdivide', 'end_subdivision',
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
    """
    Marks the start of timing, overwriting the automatic start data written on
    import, or the automatic start at the beginning of a subdivision.

    Returns:
        float: The current time.

    Raises:
        StartError: If the timer is not in a pristine state (if any stamps or
            subdivisions, must reset instead).
        StoppedError: If the timer is already stopped (must reset instead).
    """
    if f.s.cum:
        raise StartError("Already have stamps, can't start again (must reset).")
    if f.t.subdvsn_awaiting or f.t.par_subdvsn_awaiting:
        raise StartError("Already have subdivisions, can't start again (must reset).")
    if f.t.stopped:
        raise StoppedError("Timer already stopped (must open new or reset).")
    f.t.paused = False
    f.t.tmp_total = 0.  # (In case previously paused.)
    t = timer()
    f.t.start_t = t
    f.t.last_t = t
    return t


def stamp(name, unique=None, keep_subdivisions=None, quick_print=None,
          un=None, ks=None, qp=None):
    """
    Marks the end of a timing interval.

    Args:
        name: The identifier for this interval, processed through str()
        unique (None, optional): boolean, enforce uniqueness
        keep_subdivisions (None, optional): boolean, keep awaiting subdivisions
        quick_print (None, optional): boolean, print elapsed interval time
        un (None, optional): short-form for unique
        ks (None, optional): short-form for keep_subdivisions
        qp (None, optional): short-form for quick_print

        If both long- and short-form are present, they are OR'ed together.  If
        neither are present, the current global default is used.

        If keeping subdivisions, each subdivision currently awaiting
        assignment to a stamp (i.e. ended since the last stamp in this level)
        will be assigned to this one.  Otherwise, all awaiting ones will be
        discarded after aggregating their self times into the current timer.

    Returns:
        float: The current time.

    Raises:
        PausedError: If the timer is paused.
        StoppedError: If the timer is stopped.
        UniqueNameError: If uniqueness is enforced and the name provided is
            already observed at this level of the timing hierarchy.
    """
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
    """
    Marks the end of timing.  Optionally performs a stamp, hence accepts the
    same arguments.

    Args:
        name (None, optional): If used, passed to a call to stamp()
        unique (None, optional): see stamp()
        keep_subdivisions (None, optional): boolean, keep awaiting subdivisions
        quick_print (None, optional): boolean, print total time
        un (None, optional): see stamp()
        ks (None, optional): "
        qp (None, optional): "

    If keeping subdivisions and not calling a stamp, any awaiting subdivisions
    will be assigned to a special 'UNASSIGNED' position to indicate that they
    are not properly accounted for in the hierarchy (these can happen at
    different places and may be combined inadvertently).

    Returns:
        float: The current time.

    Raises:
        StoppedError: If timer already stopped.
    """
    t = timer()
    if f.t.stopped:
        raise StoppedError("Timer already stopped.")
    unique = SET['UN'] if (unique is None and un is None) else bool(unique or un)  # bool(None) becomes False
    keep_subdivisions = SET['KS'] if (keep_subdivisions is None and ks is None) else bool(keep_subdivisions or ks)
    quick_print = SET['QP'] if (quick_print is None and qp is None) else bool(quick_print or qp)
    if name is not None:
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
    """
    Pause the timer, preventing subsequent time from accumulating in the
    total.  Renders the timer inactive, disabling other timing commands.

    Returns:
        float: The current time.

    Raises:
        PausedError: If timer already paused.
        StoppedError: If timer already stopped.
    """
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
    """
    Resume a paused timer, re-activating it.  Subsequent time accumulates in
    the total.

    Returns:
        float: The current time.

    Raises:
        PausedError: If timer was not in paused state.
        StoppedError: If timer was already stopped.
    """
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
    """
    Blank stamp.  Marks the beginning of a new interval, but the elapsed time
    of the previous interval is discarded.  Intentionally the same signature
    as stamp().

    Args:
        name (None, optional): Inactive.
        unique (None, optional): Inactive.
        keep_subdivisions (bool, optional): Keep subdivisions awaiting
        quick_print (None, optional): Inactive.
        un (None, optional): Inactive.
        ks (bool, optional): see stamp().
        qp (None, optional): Inactive.

    The default for keep_subdivisions is False (does not refer to an
    adjustable global setting), meaning that any subdivisons awaiting would be
    discarded after having their self times aggregated into this timer.  If
    this is set to True, subdivisions are put in the 'UNASSIGNED' position,
    indicating they are not properly accounted for in the hierarchy.

    Returns:
        float: The current time.

    Raises:
        StoppedError: If timer is already stopped.
    """
    t = timer()
    if f.t.stopped:
        raise StoppedError("Cannot b_stamp stopped timer.")
    keep_subdivisions = (keep_subdivisions or ks)
    times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    f.t.last_t = timer()
    f.t.self_cut += f.t.last_t - t
    return t


def reset():
    """
    Resets the timer at the current level in the hierarchy (i.e. might or
    might not be the root).

    Erases timing data but preserves relationship to the hierarchy.  If the
    current timer level was not previously stopped, any timing data from this
    timer (including subdivisions) will be discarded and not added to the next
    higher level in the data structure.  If the current timer was previously
    stopped, then its data has already been pushed into the next higher level.

    Returns:
        float: The current time.

    Raises:
        LoopError: If in a timed loop.
    """
    if f.t.in_loop:
        raise LoopError("Cannot reset a timer while it is in timed loop.")
    f.t.reset()
    f.refresh_shortcuts()
    return f.t.start_t


#
# Timer hierarchy.
#


@opt_arg_wrap
def wrap(func, subdivide=True, name=None, rgstr_stamps=None, save_itrs=None):
    """
    Decorator function for automatically inducing a subdivision on entering a
    subfunction or method.  Can be used (as @gtimer.wrap) with or without any
    arguments.

    Args:
        func (callable): Function to be decorated.
        subdivide (bool, optional): To subdivide.
        name (None, optional): Identifier for the subdivision, passed through
            str()
        rgstr_stamps (None, optional): List or tuple of identifiers.
        save_itrs (None, optional): bool, to save individual iterations.

    If subdivide is False, then the wrapper does nothing but return the
    provided function.

    If a name is not provided, the function's __name__ is used (recommended).

    For the other options, see subdivide().

    Returns:
        callable: A new function or method with timing hierarchy management
            surrounding a call to the original function.
    """
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
    """
    Induces a new subdivision--a lower level in the timing hierarchy.
    Subsequent calls to methods like stamp() operate on this new level.

    Args:
        name: Identifer for the new timer, passed through str().
        rgstr_stamps (None, optional): List or tuple of identifiers.
        save_itrs (TYPE, optional): bool, Save individual iteration data.

    If rgstr_stamps is used, the collection is passed through set() for
    uniqueness, and the each entry is passed through str().  Any identifiers
    contained within are guaranteed to exist in the final dictionaries of
    stamp data when this timer closes. If any registered stamp was not
    actually encountered, zero values are populated.  (Can be useful if a
    subdivision is called repeatedly with conditional stamps.)

    The save_itrs input defaults to the current global default.  If save_itrs
    is True, then whenever another subdivision by the same name is added to
    the same position in the parent timer, and the two data structures are
    merged, any stamps present only as individual stamps (but not as itrs)
    will be made into itrs, with each subsequent data dump (when a subdivision
    is stopped) treated as another iteration.  (Consider multiple calls to a
    timer-wrapped subfunction within a loop.)  Actually, only the value of
    this setting on the first such subdivision attached to the parent timer
    dictates the behavior during all subsequent merges.  This setting does not
    affect any other timers in the hierarchy.

    Returns:
        None
    """
    _auto_subdivide(name, rgstr_stamps, save_itrs)
    f.t.is_user_subdvsn = True


def end_subdivision():
    """
    Ends a user-induced timing subdivision, returning the previous level in
    the timing hierarchy as the target of timing commands such as stamp().
    Includes a call to stop(), although a previous call to stop() does no
    harm.

    Returns:
        None

    Raises:
        GTimerError: If current subdivision was not induced by user.
        LoopError: If current timer is in a timed loop.
    """
    if not f.t.is_user_subdvsn:
        raise GTimerError('Attempted to end a subdivision not started by user.')
    if f.t.in_loop:
        raise LoopError('Cannot close a timer while it is in timed loop.')
    _close_subdivision()


#
# Functions operating on the root timer.
#


def rename_root(name):
    """
    Rename the root timer (regardless of current timing level).

    Args:
        name: Identifier, passed through str()

    Returns:
        str: Implemented identifier.
    """
    name = str(name)
    f.root.name = name
    f.root.times.name = name
    return name


def set_save_itrs_root(setting):
    """
    Adjust the root timer save_itrs setting, such as for use in
    multiprocessing, when a root timer may become a parallel subdivision (see
    subdivide()).

    Args:
        setting: Save individual iterations data, passed through bool()

    Returns:
        bool: Implemented setting value.
    """
    setting = bool(setting)
    f.root.times.save_itrs = setting
    return setting


def rgstr_stamps_root(rgstr_stamps):
    """
    Register stamps with the root timer (see subdivision()).

    Args:
        rgstr_stamps (list, tuple): Collection of identifiers, passed through
            set(), then each is passed through str().

    Returns:
        list: Implemented registered stamp collection.
    """
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    f.root.rgstr_stamps = rgstr_stamps
    return rgstr_stamps


def reset_root():
    """
    CAUTION: A HARD RESET.  Re-instantiates the entire underlying timer data
    structure and restarts (same as first import), discarding all previous
    state and data.  No hazard checks--always executes when called, any time,
    anywhere.

    Returns:
        None
    """
    f.hard_reset()


#
# Timer status queries.
#


def is_timer_stopped():
    """
    Check whether the current timer level is stopped.

    Returns:
        bool: True if stopped.
    """
    return f.t.stopped


def is_timer_paused():
    """
    Check whether the current timer level is paused.

    Returns:
        bool: True if paused.
    """
    return f.t.paused


def has_subdvsn_awaiting():
    """
    Check whether the current timer level has any subdivisions awaiting
    assignment (at the next stamp).

    Returns:
        bool: True if any.
    """
    return bool(f.t.subvsn_awaiting)


def has_par_subdvsn_awaiting():
    """
    Check whether the current timer level has any parallel subdivisions
    awaiting assignment (at the next stamp).

    Returns:
        bool: True if any.
    """
    return bool(f.t.par_subdvsn_awaiting)


def get_active_lineage():
    """
    Query the lineage of the current timer level.  Provides only timer names,
    not stamp names (as these have not been decided yet!).

    Returns:
        str: Formatted sequence of timer names in one string.
    """
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
    """
    Set the global default (henceforth) behavior whether to save individual
    iteration data of new subdivisions and loops.

    Args:
        setting: Passed through bool().

    Returns:
        bool: Implemented setting value.
    """
    setting = bool(setting)
    SET['SI'] = setting
    return setting


def set_def_keep_subdivisions(setting):
    """
    Set the global default (henceforth) behavior whether to keep awaiting
    subdivisions when stamping.

    Args:
        setting: Passed through bool().

    Returns:
        bool: Implemented setting value.
    """
    setting = bool(setting)
    SET['KS'] = setting
    return setting


def set_def_quick_print(setting):
    """
    Set the global default (henceforth) behavior whether to quick print
    when stamping or stopping.

    Args:
        setting: Passed through bool().

    Returns:
        bool: Implemented setting value.
    """
    setting = bool(setting)
    SET['QP'] = setting
    return setting


def set_def_unique(setting):
    """
    Set the global default (henceforth) behavior whether to enforce unique
    stamp names (recommended).

    Args:
        setting: Passed through bool().

    Returns:
        bool: Implemented setting value.
    """
    setting = bool(setting)
    SET['UN'] = setting
    return setting


#
# Drop awaiting subdivisions.
#


def clear_subdvsn_awaiting():
    """
    Remove all currently awaiting subdivisions, before aggregating self time.

    Returns:
        None
    """
    f.t.subdvsn_awaiting.clear()


def clear_par_subdvsn_awaiting():
    """
    Remove all currently awaiting parallel subdivisions, before aggregating self time.

    Returns:
        None
    """
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
