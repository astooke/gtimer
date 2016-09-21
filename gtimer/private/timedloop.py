
"""
Classes which comprise the timed loops.
"""
from __future__ import absolute_import

from gtimer.private import loop
from gtimer.private.focus import get_current_timer
from gtimer.local.util import sanitize_rgstr_stamps
from gtimer.local.exceptions import LoopError


class TimedLoopBase(object):
    """Base class, not to be used."""

    def __init__(self,
                 name=None,
                 rgstr_stamps=None,
                 save_itrs=True,
                 loop_end_stamp=None,
                 end_stamp_unique=True,
                 keep_prev_subdivisions=True,
                 keep_end_subdivisions=True,
                 quick_print=False):
        self._name = None if name is None else str(name)
        self._rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
        self._save_itrs = bool(save_itrs)
        self._loop_end_stamp = None if loop_end_stamp is None else str(loop_end_stamp)
        self._end_stamp_unique = end_stamp_unique,
        self._keep_prev_subdivisions = keep_prev_subdivisions
        self._keep_end_subdivisions = keep_end_subdivisions
        self._quick_print = quick_print
        self._started = False
        self._exited = False

    def __enter__(self):
        if self._exited:
            raise LoopError("Loop used as context manager previously exited (make a new one).")
        return self

    def __exit__(self, *args):
        if not self._exited:
            if self._started:
                loop.loop_end(self._loop_end_stamp,
                              self._end_stamp_unique,
                              self._keep_end_subdivisions,
                              self._quick_print)
            loop.exit_loop()
        self._exited = True

    def exit(self):
        self.__exit__()


class TimedLoop(TimedLoopBase):

    def __init__(self, *args, **kwargs):
        self._first = True
        super(TimedLoop, self).__init__(*args, **kwargs)

    def next(self):
        if self._exited:
            raise LoopError("Attempted loop iteration on already exited loop (need a new loop object).")
        if self._first:
            loop.enter_loop(self._name,
                            self._rgstr_stamps,
                            self._save_itrs,
                            self._keep_prev_subdivisions)
            self._first = False
            self._started = True
            self._timer = get_current_timer()
        else:
            if get_current_timer() is not self._timer:
                raise LoopError("Loop timer mismatch, likely improper subdivision during loop (cannot span iterations).")
            loop.loop_end(self._loop_end_stamp,
                          self._end_stamp_unique,
                          self._keep_end_subdivisions,
                          self._quick_print)
        loop.loop_start()

    __next__ = next


class TimedFor(TimedLoopBase):

    def __init__(self, iterable, *args, **kwargs):
        self._iterable = iterable
        super(TimedFor, self).__init__(*args, **kwargs)

    def __iter__(self):
        if self._exited:
            raise LoopError("For-loop object already exited (need a new loop object).")
        loop.enter_loop(self._name,
                        self._rgstr_stamps,
                        self._save_itrs,
                        self._keep_prev_subdivisions)
        self._timer = get_current_timer()
        for i in self._iterable:
            loop.loop_start()
            self._started = True
            yield i
            if self._exited:
                raise LoopError("Loop mechanism exited improperly (must break).")
            if get_current_timer() is not self._timer:
                raise LoopError("Loop timer mismatch, likely improper subdivision during loop (cannot span iterations).")
            loop.loop_end(self._loop_end_stamp,
                          self._end_stamp_unique,
                          self._keep_end_subdivisions)
            self._started = False
        loop.exit_loop()
        self._exited = True
