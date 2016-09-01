# Need to import the loop functions.

from gtimer.private import mgmt
from gtimer.private.util import get_current_timer


class TimedLoopBase(object):
    """Base class, not to be used."""

    def __init__(self,
                 name=None,
                 rgstr_stamps=list(),
                 save_itrs=True,
                 loop_end_stamp=None,
                 end_stamp_unique=True,
                 keep_prev_subdivisions=True,
                 keep_end_subdivisions=True):
        self._name = None if name is None else str(name)
        self._rgstr_stamps = mgmt_priv.sanitize_rgstr_stamps(rgstr_stamps)
        self._save_itrs = bool(save_itrs)
        self._loop_end_stamp = None if loop_end_stamp is None else str(loop_end_stamp)
        self._end_stamp_unique = end_stamp_unique,
        self._keep_prev_subdivisions = keep_prev_subdivisions
        self._keep_end_subdivisions = keep_end_subdivisions
        self._started = False
        self._exited = False

    def __enter__(self):
        if self._exited:
            return RuntimeError("Loop used as context manager previously exited (make a new one).")
        return self

    def __exit__(self, *args):
        if not self._exited:
            if self._started:
                mgmt.loop_end(self._loop_end_stamp,
                            self._end_stamp_unique,
                            self._keep_end_subdivisions)
            mgmt.exit_loop()
        self._exited = True

    def exit(self):
        self.__exit__()


class TimedLoop(TimedLoopBase):

    def __init__(self, current_timer, *args, **kwargs):
        self._first = True
        self._current_timer = current_timer
        super(TimedLoop, self).__init__(*args, **kwargs)

    def next(self):
        if self._exited:
            raise RuntimeError("Loop already exited (need a new loop object).")
        if self._first:
            mgmt.enter_loop(self._name,
                          self._rgstr_stamps,
                          self._save_itrs,
                          self._keep_prev_subdivisions)
            self._first = False
            self._started = True
            self._timer = get_current_timer()
        else:
            if get_current_timer() is not self._timer:
                raise RuntimeError("Loop timer mismatch, likely improper subdivision during loop, spans iterations.")
            mgmt.loop_end(self._loop_end_stamp,
                        self._end_stamp_unique,
                        self._keep_end_subdivisions)
        mgmt.loop_start()


class TimedFor(TimedLoopBase):

    def __init__(self, iterable, *args, **kwargs):
        self._iterable = iterable
        super(TimedFor, self).__init__(*args, **kwargs)

    def __iter__(self):
        if self._exited:
            raise RuntimeError("For-loop object already used, need a different one.")
        mgmt.enter_loop(self._name,
                      self._rgstr_stamps,
                      self._save_itrs,
                      self._keep_prev_subdivisions)
        self._timer = get_current_timer()
        for i in self._iterable:
            mgmt.loop_start()
            self._started = True
            yield i
            if self._exited:
                raise RuntimeError("Loop mechanism exited improperly while in loop.")
            if get_current_timer() is not self._timer:
                raise RuntimeError("Loop timer mismatch, likely improper subdivision during loop, spans iterations.")
            mgmt.loop_end(self._loop_end_stamp,
                        self._end_stamp_unique,
                        self._keep_end_subdivisions)
            self._started = False
        mgmt.exit_loop()
        self._exited = True
