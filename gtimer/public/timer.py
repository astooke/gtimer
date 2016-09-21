
"""
Core timer functionality provided to user.
"""
from __future__ import absolute_import, print_function
from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.private import times as times_priv
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.util import opt_arg_wrap
from gtimer.private.const import UNASGN
from gtimer.local.exceptions import (StartError, StoppedError, PausedError,
                                     LoopError, GTimerError, UniqueNameError,
                                     BackdateError)


__all__ = ['start', 'stamp', 'stop', 'pause', 'resume', 'blank_stamp', 'reset', 'current_time',
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


def start(backdate=None):
    """
    Mark the start of timing, overwriting the automatic start data written on
    import, or the automatic start at the beginning of a subdivision.

    Notes:
        Backdating: For subdivisions only.  Backdate time must be in the past
        but more recent than the latest stamp in the parent timer.

    Args:
        backdate (float, optional): time to use for start instead of current.

    Returns:
        float: The current time.

    Raises:
        BackdateError: If given backdate time is out of range or used in root timer.
        StartError: If the timer is not in a pristine state (if any stamps or
            subdivisions, must reset instead).
        StoppedError: If the timer is already stopped (must reset instead).
        TypeError: If given backdate value is not type float.
    """
    if f.s.cum:
        raise StartError("Already have stamps, can't start again (must reset).")
    if f.t.subdvsn_awaiting or f.t.par_subdvsn_awaiting:
        raise StartError("Already have subdivisions, can't start again (must reset).")
    if f.t.stopped:
        raise StoppedError("Timer already stopped (must open new or reset).")
    t = timer()
    if backdate is None:
        t_start = t
    else:
        if f.t is f.root:
            raise BackdateError("Cannot backdate start of root timer.")
        if not isinstance(backdate, float):
            raise TypeError("Backdate must be type float.")
        if backdate > t:
            raise BackdateError("Cannot backdate to future time.")
        if backdate < f.tm1.last_t:
            raise BackdateError("Cannot backdate start to time previous to latest stamp in parent timer.")
        t_start = backdate
    f.t.paused = False
    f.t.tmp_total = 0.  # (In case previously paused.)
    f.t.start_t = t_start
    f.t.last_t = t_start
    return t


def stamp(name, backdate=None,
          unique=None, keep_subdivisions=None, quick_print=None,
          un=None, ks=None, qp=None):
    """
    Mark the end of a timing interval.

    Notes:
        If keeping subdivisions, each subdivision currently awaiting
        assignment to a stamp (i.e. ended since the last stamp in this level)
        will be assigned to this one.  Otherwise, all awaiting ones will be
        discarded after aggregating their self times into the current timer.

        If both long- and short-form are present, they are OR'ed together.  If
        neither are present, the current global default is used.

        Backdating: record a stamp as if it happened at an earlier time.
        Backdate time must be in the past but more recent than the latest stamp.
        (This can be useful for parallel applications, wherein a sub- process
        can return times of interest to the master process.)

    Warning:
        When backdating, awaiting subdivisions will be assigned as normal, with
        no additional checks for validity.

    Args:
        name (any): The identifier for this interval, processed through str()
        backdate (float, optional): time to use for stamp instead of current
        unique (bool, optional): enforce uniqueness
        keep_subdivisions (bool, optional): keep awaiting subdivisions
        quick_print (bool, optional): print elapsed interval time
        un (bool, optional): short-form for unique
        ks (bool, optional): short-form for keep_subdivisions
        qp (bool, optional): short-form for quick_print

    Returns:
        float: The current time.

    Raises:
        BackdateError: If the given backdate time is out of range.
        PausedError: If the timer is paused.
        StoppedError: If the timer is stopped.
        TypeError: If the given backdate value is not type float.
    """
    t = timer()
    if f.t.stopped:
        raise StoppedError("Cannot stamp stopped timer.")
    if f.t.paused:
        raise PausedError("Cannot stamp paused timer.")
    if backdate is None:
        t_stamp = t
    else:
        if not isinstance(backdate, float):
            raise TypeError("Backdate must be type float.")
        if backdate > t:
            raise BackdateError("Cannot backdate to future time.")
        if backdate < f.t.last_t:
            raise BackdateError("Cannot backdate to time earlier than last stamp.")
        t_stamp = backdate
    elapsed = t_stamp - f.t.last_t
    # Logic: default unless either arg used.  if both args used, 'or' them.
    unique = SET['UN'] if (unique is None and un is None) else bool(unique or un)  # bool(None) becomes False
    keep_subdivisions = SET['KS'] if (keep_subdivisions is None and ks is None) else bool(keep_subdivisions or ks)
    quick_print = SET['QP'] if (quick_print is None and qp is None) else bool(quick_print or qp)
    _stamp(name, elapsed, unique, keep_subdivisions, quick_print)
    tmp_self = timer() - t
    f.t.self_cut += tmp_self
    f.t.last_t = t_stamp + tmp_self
    return t


def stop(name=None, backdate=None,
         unique=None, keep_subdivisions=None, quick_print=None,
         un=None, ks=None, qp=None):
    """
    Mark the end of timing.  Optionally performs a stamp, hence accepts the
    same arguments.

    Notes:
        If keeping subdivisions and not calling a stamp, any awaiting subdivisions
        will be assigned to a special 'UNASSIGNED' position to indicate that they
        are not properly accounted for in the hierarchy (these can happen at
        different places and may be combined inadvertently).

        Backdating: For subdivisions only.  Backdate time must be in the past
        but more recent than the latest stamp.

    Args:
        name (any, optional): If used, passed to a call to stamp()
        backdate (float, optional): time to use for stop instead of current
        unique (bool, optional): see stamp()
        keep_subdivisions (bool, optional): keep awaiting subdivisions
        quick_print (bool, optional): boolean, print total time
        un (bool, optional): see stamp()
        ks (bool, optional): see stamp()
        qp (bool, optional): see stamp()


    Returns:
        float: The current time.

    Raises:
        BackdateError: If given backdate is out of range, or if used in root timer.
        PausedError: If attempting stamp in paused timer.
        StoppedError: If timer already stopped.
        TypeError: If given backdate value is not type float.
    """
    t = timer()
    if f.t.stopped:
        raise StoppedError("Timer already stopped.")
    if backdate is None:
        t_stop = t
    else:
        if f.t is f.root:
            raise BackdateError("Cannot backdate stop of root timer.")
        if not isinstance(backdate, float):
            raise TypeError("Backdate must be type float.")
        if backdate > t:
            raise BackdateError("Cannot backdate to future time.")
        if backdate < f.t.last_t:
            raise BackdateError("Cannot backdate to time earlier than last stamp.")
        t_stop = backdate
    unique = SET['UN'] if (unique is None and un is None) else bool(unique or un)  # bool(None) becomes False
    keep_subdivisions = SET['KS'] if (keep_subdivisions is None and ks is None) else bool(keep_subdivisions or ks)
    quick_print = SET['QP'] if (quick_print is None and qp is None) else bool(quick_print or qp)
    if name is not None:
        if f.t.paused:
            raise PausedError("Cannot stamp paused timer.")
        elapsed = t_stop - f.t.last_t
        _stamp(name, elapsed, unique, keep_subdivisions, quick_print)
    else:
        times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    for s in f.t.rgstr_stamps:
        if s not in f.s.cum:
            f.s.cum[s] = 0.
            f.s.order.append(s)
    if not f.t.paused:
        f.t.tmp_total += t_stop - f.t.start_t
    f.t.tmp_total -= f.t.self_cut
    f.t.self_cut += timer() - t  # AFTER subtraction from tmp_total, before dump
    times_priv.dump_times()
    f.t.stopped = True
    if quick_print:
        print("({}) Total: {:.4f}".format(f.t.name, f.r.total))
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


def blank_stamp(name=None, backdate=None,
                unique=None, keep_subdivisions=False, quick_print=None,
                un=None, ks=False, qp=None):
    """
    Mark the beginning of a new interval, but the elapsed time
    of the previous interval is discarded.  Intentionally the same signature
    as stamp().

    Notes:
        The default for keep_subdivisions is False (does not refer to an
        adjustable global setting), meaning that any subdivisons awaiting would be
        discarded after having their self times aggregated into this timer.  If
        this is set to True, subdivisions are put in the 'UNASSIGNED' position,
        indicating they are not properly accounted for in the hierarchy.

    Args:
        name (any, optional): Inactive.
        backdate (any, optional): Inactive.
        unique (any, optional): Inactive.
        keep_subdivisions (bool, optional): Keep subdivisions awaiting
        quick_print (any, optional): Inactive.
        un (any, optional): Inactive.
        ks (bool, optional): see stamp().
        qp (any, optional): Inactive.

    Returns:
        float: The current time.

    Raises:
        StoppedError: If timer is already stopped.
    """
    t = timer()
    if f.t.stopped:
        raise StoppedError("Cannot blank_stamp stopped timer.")
    keep_subdivisions = (keep_subdivisions or ks)
    times_priv.assign_subdivisions(UNASGN, keep_subdivisions)
    f.t.last_t = timer()
    f.t.self_cut += f.t.last_t - t
    return t


def reset():
    """
    Reset the timer at the current level in the hierarchy (i.e. might or
    might not be the root).

    Notes:
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


def current_time():
    """
    Returns the current time using timeit.default_timer() (same as used
    throughout gtimer).

    Returns:
        float: the current time
    """
    return timer()


#
# Timer hierarchy.
#


@opt_arg_wrap
def wrap(func, subdivide=True, name=None, rgstr_stamps=None, save_itrs=None):
    """
    Decorator function which can automatically induce a subdivision on
    entering a subfunction or method.  Can be used (as @gtimer.wrap) with or
    without any arguments.

    Notes:
        If subdivide is False, then the wrapper does nothing but return the
        provided function.

        If a name is not provided, the function's __name__ is used (recommended).

        For the other options, see subdivide().

    Args:
        func (callable): Function to be decorated.
        subdivide (bool, optional): To subdivide.
        name (any, optional): Identifier for the subdivision, passed through str()
        rgstr_stamps (list,tuple, optional): Identifiers.
        save_itrs (bool, optional): to save individual iterations.

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
    Induce a new subdivision--a lower level in the timing hierarchy.
    Subsequent calls to methods like stamp() operate on this new level.

    Notes:
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
        timer-wrapped subfunction within a loop.)  This setting does not
        affect any other timers in the hierarchy.

    Args:
        name (any): Identifer for the new timer, passed through str().
        rgstr_stamps (list,tuple, optional): Identifiers.
        save_itrs (bool, optional): Save individual iteration data.


    Returns:
        None
    """
    _auto_subdivide(name, rgstr_stamps, save_itrs)
    f.t.is_user_subdvsn = True


def end_subdivision():
    """
    End a user-induced timing subdivision, returning the previous level in
    the timing hierarchy as the target of timing commands such as stamp().
    Includes a call to stop(); a previous call to stop() is OK.

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
        name (any): Identifier, passed through str()

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
        setting (bool): Save individual iterations data, passed through bool()

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
    Re-instantiate the entire underlying timer data structure and restart
    (same as first import), discarding all previous state and data.

    Warning:
        This is a hard reset without hazard checks--always executes when
        called, any time, anywhere.

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


def _stamp(name, elapsed, unique, keep_subdivisions, quick_print):
    name = str(name)
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
    if quick_print:
        print("({}) {}: {:.4f}".format(f.t.name, name, elapsed))
    times_priv.assign_subdivisions(name, keep_subdivisions)


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
