
"""
Almost everything to do with loops (some visible to from user).
"""

from timeit import default_timer as timer
import data_glob as g
import times_glob
import timer_mgmt


__all__ = ['timed_for', 'timed_loop']


#
# Hidden from user.
#


class Loop(object):
    """Hold info for name checking and assigning."""

    def __init__(self, name=None, rgstr_stamps=list()):
        self.name = None if name is None else str(name)
        self.stamps = list()
        self.rgstr_stamps = rgstr_stamps
        self.itr_stamp_used = dict()
        for s in rgstr_stamps:
            self.itr_stamp_used[s] = False


class TimedLoopBase(object):
    """Base class, not to be used."""

    def __init__(self, name=None, rgstr_stamps=list()):
        self._name = name
        self._rgstr_stamps = timer_mgmt.sanitize_rgstr_stamps(rgstr_stamps)
        self._started = False
        self._exited = False

    def __enter__(self):
        if self._exited:
            return RuntimeError("Loop used as context manager previously exited (make a new one).")
        return self

    def __exit__(self, *args):
        if not self._exited:
            if self._started:
                loop_end()
            exit_loop()
        self._exited = True

    def exit(self):
        self.__exit__()


#
# Exposed to user.
#


class timed_loop(TimedLoopBase):

    def __init__(self, name=None, rgstr_stamps=list()):
        self._first = True
        super(timed_loop, self).__init__(name, rgstr_stamps)

    def next(self):
        if self._exited:
            raise RuntimeError("Loop already exited (make a new loop).")
        if self._first:
            enter_loop(self._name, self._rgstr_stamps)
            self._first = False
            self._started = True
        else:
            loop_end()
        loop_start()


class timed_for(TimedLoopBase):

    def __init__(self, iterable, name=None, rgstr_stamps=list()):
        self._iterable = iterable
        super(timed_for, self).__init__(name, rgstr_stamps)

    def __iter__(self):
        enter_loop(self._name, self._rgstr_stamps)
        for i in self._iterable:
            loop_start()
            self._started = True
            yield i
            if self._exited:
                raise RuntimeError("Loop mechanism exited improperly while in loop.")
            loop_end()
            self._started = False
        exit_loop()
        self._exited = True


#
# Hidden from user.
#


def enter_loop(name=None, rgstr_stamps=list()):
    t = timer()
    g.tf.last_t = t
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    if g.tf.children_awaiting:
        times_glob.l_assign_children(g.UNASGN)
    if name is not None:  # Entering a named loop.
        if g.tf.loop_depth < 1 or name not in g.lf.stamps:
            if name in g.sf.cum:
                raise ValueError("Duplicate name given to loop: {}".format(name))
            g.sf.cum[name] = 0.
            g.sf.itrs[name] = []
            g.sf.order.append(name)
        if g.tf.loop_depth > 0 and name not in g.lf.stamps:
            g.lf.stamps.append(name)
        t = timer()
        g.rf.self_cut += t - g.tf.last_t
        timer_mgmt.open_named_loop_timer(name, rgstr_stamps)  # (should be OK empty list for rgstr_stamps)
    else:  # Entering an anonymous loop.
        g.tf.loop_depth += 1
    g.create_next_loop(name, rgstr_stamps)
    g.rf.self_cut += timer() - t


def loop_start():
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer cannot be paused when entering next loop iteration.")
    for k in g.lf.itr_stamp_used:
        g.lf.itr_stamp_used[k] = False


def loop_end():
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    g.tf.last_t = t
    for s in g.lf.rgstr_stamps:
        if not g.lf.itr_stamp_used[s]:
            if s not in g.lf.stamps:
                g.lf.stamps.append(s)
                g.sf.cum[s] = 0.
                g.sf.itrs[s] = []
                g.sf.order.append(s)
            g.sf.itrs.append(0.)
    if g.tf.children_awaiting:
        times_glob.l_assign_children(g.UNASGN)
    if g.lf.name is not None:
        # Reach back and stamp in the parent timer.
        g.focus_backward_timer()
        elapsed = t - g.tf.last_t
        g.sf.cum[g.lf.name] += elapsed
        g.sf.itrs[g.lf.name].append(elapsed)
        g.tf.last_t = t
        g.focus_forward_timer()
    g.rf.self_cut += timer() - t


def exit_loop():
    t = timer()
    if g.tf.stopped:
        raise RuntimeError("Timer already stopped.")
    if g.tf.paused:
        raise RuntimeError("Timer paused.")
    if g.lf.name is not None:
        timer_mgmt.close_last_timer()
        if g.tf.children_awaiting:
            times_glob.l_assign_children(g.lf.name)
    else:
        g.tf.loop_depth -= 1
        if g.tf.children_awaiting:
            times_glob.l_assign_children(g.UNASGN)
    g.remove_last_loop()
    g.rf.self_cut += timer() - t
