
"""
Class which holds temporary timing data which does not need to persis after
timing is complete.
"""

from timeit import default_timer as timer
import copy

from gtimer.local.times import Times


class Timer(object):
    """ Current (temporary) values describing state of timer.
    (Disappears or irrelevant after timing is complete.)
    """

    def __init__(self,
                 name,
                 rgstr_stamps=None,
                 dump=None,
                 is_named_loop=False,
                 in_loop=False,
                 **kwargs):
        self.name = str(name)
        self.rgstr_stamps = rgstr_stamps if rgstr_stamps is not None else list()
        self.dump = dump  # refers to a Times instance, not a Timer instance
        self.is_named_loop = is_named_loop  # needed for restoring dump after deepcopy
        self.in_loop = bool(in_loop)
        self.times = None
        self.is_user_subdvsn = False
        self.reset()
        self.times = Times(name, **kwargs)

    def __deepcopy__(self, memo):
        new = type(self)(self.name)
        new.__dict__.update(self.__dict__)
        new.subdvsn_awaiting = copy.deepcopy(self.subdvsn_awaiting, memo)
        new.par_subdvsn_awaiting = copy.deepcopy(self.par_subdvsn_awaiting, memo)
        for _, sub_times in new.subdvsn_awaiting.iteritems():
            sub_times.parent = new.times
        for _, sub_list in new.par_subdvsn_awaiting.iteritems():
            for sub_times in sub_list:
                sub_times.parent = new.times
        new.times = copy.deepcopy(self.times, memo)
        # Dump needs rest of stack, see mgmt_priv.copy_timer_stack()
        new.dump = None
        return new

    def reset(self):
        self.stopped = False
        self.paused = False
        self.tmp_total = 0.
        self.self_cut = 0.
        self.subdvsn_awaiting = dict()
        self.par_subdvsn_awaiting = dict()
        self.start_t = timer()
        self.last_t = self.start_t
        if self.times is not None:
            self.times.reset()
