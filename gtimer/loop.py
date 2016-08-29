
"""
Almost everything to do with loops (some visible to from user).
"""

from timeit import default_timer as timer
import data_glob as g
import times_glob
import timer_glob
import mgmt_priv
import mgmt_pub

__all__ = ['timed_loop', 'timed_for']


#
# Expose to user.
#


def timed_loop(name=None,
               rgstr_stamps=list(),
               save_itrs=True,
               loop_end_stamp=None,
               end_stamp_unique=True,
               keep_prev_subdivisions=True,
               keep_end_subdivisions=True):
    return TimedLoop(name=name,
                     rgstr_stmps=rgstr_stamps,
                     save_itrs=save_itrs,
                     loop_end_stamp=loop_end_stamp,
                     end_stamp_unique=end_stamp_unique,
                     keep_prev_subdivisions=keep_prev_subdivisions,
                     keep_end_subdivisions=keep_end_subdivisions)


def timed_for(iterable,
              name=None,
              rgstr_stamps=list(),
              save_itrs=True,
              loop_end_stamp=None,
              end_stamp_unique=True,
              keep_prev_subdivisions=True,
              keep_end_subdivisions=True):
    return TimedFor(iterable,
                    name=name,
                    rgstr_stamps=rgstr_stamps,
                    save_itrs=save_itrs,
                    loop_end_stamp=loop_end_stamp,
                    end_stamp_unique=end_stamp_unique,
                    keep_prev_subdivisions=keep_prev_subdivisions,
                    keep_end_subdivisions=keep_end_subdivisions)


#
# Hidden from user.
#


class Loop(object):
    """Hold info for name checking and assigning."""

    def __init__(self, name=None, rgstr_stamps=list(), save_itrs=True):
        self.name = None if name is None else str(name)
        self.stamps = list()
        self.rgstr_stamps = rgstr_stamps
        self.itr_stamp_used = dict()
        for s in rgstr_stamps:
            self.itr_stamp_used[s] = False
        self.save_itrs = save_itrs


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
        self._name = str(name)
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
                loop_end(self._loop_end_stamp,
                         self._end_stamp_unique,
                         self._keep_end_subdivisions)
            exit_loop()
        self._exited = True

    def exit(self):
        self.__exit__()


class TimedLoop(TimedLoopBase):

    def __init__(self, *args, **kwargs):
        self._first = True
        super(TimedLoop, self).__init__(*args, **kwargs)

    def next(self):
        if self._exited:
            raise RuntimeError("Loop already exited (need a new loop object).")
        if self._first:
            enter_loop(self._name,
                       self._rgstr_stamps,
                       self._save_itrs,
                       self._keep_prev_subdivisions)
            self._first = False
            self._started = True
            self._timer = g.tf
        else:
            if g.tf is not self._timer:
                raise RuntimeError("Loop timer mismatch, likely improper subdivision during loop, spans iterations.")
            loop_end(self._loop_end_stamp,
                     self._end_stamp_unique,
                     self._keep_end_subdivisions)
        loop_start()


class TimedFor(TimedLoopBase):

    def __init__(self, iterable, *args, **kwargs):
        self._iterable = iterable
        super(TimedFor, self).__init__(*args, **kwargs)

    def __iter__(self):
        if self._exited:
            raise RuntimeError("For-loop object already used, need a different one.")
        enter_loop(self._name,
                   self._rgstr_stamps,
                   self._save_itrs,
                   self._keep_prev_subdivisions)
        self._timer = g.tf
        for i in self._iterable:
            loop_start()
            self._started = True
            yield i
            if self._exited:
                raise RuntimeError("Loop mechanism exited improperly while in loop.")
            if g.tf is not self._timer:
                raise RuntimeError("Loop timer mismatch, likely improper subdivision during loop, spans iterations.")
            loop_end(self._loop_end_stamp,
                     self._end_stamp_unique,
                     self._keep_end_subdivisions)
            self._started = False
        exit_loop()
        self._exited = True


def enter_loop(name=None,
               rgstr_stamps=list(),
               save_itrs=True,
               keep_subidivisions=True):
    print "enter_loop"
    t = timer()
    g.tf.last_t = t
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    if keep_subidivisions:
        if g.tf.subdivisions_awaiting:
            times_glob.assign_subdivisions(g.UNASGN)
        if g.tf.par_subdivisions_awaiting:
            times_glob.par_assign_subdivisions(g.UNASGN)
    if name is None:  # Entering anonynous loop.
        if g.tf.in_loop:
            raise RuntimeError("Entering anonymous inner timed loop (not supported).")
        g.tf.in_loop = True
    else:  # Entering a named loop.
        if not g.tf.in_loop or name not in g.lf.stamps:
            if name in g.sf.cum:
                raise ValueError("Duplicate name given to loop: {}".format(name))
            g.sf.cum[name] = 0.
            g.sf.itrs[name] = []
            g.sf.order.append(name)
        if g.tf.in_loop and name not in g.lf.stamps:
            g.lf.stamps.append(name)
        t = timer()
        g.rf.self_cut += t - g.tf.last_t
        mgmt_priv.subdivide_named_loop(name, rgstr_stamps, save_itrs)
    g.create_next_loop(name, rgstr_stamps, save_itrs)
    g.rf.self_cut += timer() - t


def loop_start():
    print "loop_start"
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    for k in g.lf.itr_stamp_used:
        g.lf.itr_stamp_used[k] = False


def loop_end(loop_end_stamp=None,
             end_stamp_unique=True,
             keep_subdivisions=True):
    print "loop_end"
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if loop_end_stamp is not None:
        t = timer_glob.stamp(loop_end_stamp,
                             end_stamp_unique,
                             keep_subdivisions)
    else:
        t = timer()
        g.tf.last_t = t
        if keep_subdivisions:
            if g.tf.subdivisions_awaiting:
                times_glob.assign_subdivisions(g.UNASGN)
            if g.tf.par_subdivisions_awaiting:
                times_glob.par_assign_subdivisions(g.UNASGN)
    for s in g.lf.rgstr_stamps:
        if not g.lf.itr_stamp_used[s]:
            if s not in g.lf.stamps:
                g.lf.stamps.append(s)
                g.sf.cum[s] = 0.
                if g.lf.save_itrs:
                    g.sf.itrs[s] = []
                g.sf.order.append(s)
            if g.lf.save_itrs:
                g.sf.itrs.append(0.)
    if g.lf.name is not None:
        # Reach back and stamp in the parent timer.
        g.focus_backward_timer()
        elapsed = t - g.tf.last_t
        g.sf.cum[g.lf.name] += elapsed
        if g.lf.save_itrs:  # do NOT focus_backward_loop()
            g.sf.itrs[g.lf.name].append(elapsed)
        g.tf.last_t = t
        g.focus_forward_timer()
    g.rf.self_cut += timer() - t


def exit_loop():
    print "exit_loop"
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused at loop exit (uncertain behavior--not allowed).")
    g.tf.in_loop = False
    if g.lf.name is not None:
        mgmt_priv.end_subdivision()
    g.remove_last_loop()
    g.rf.self_cut += timer() - t
