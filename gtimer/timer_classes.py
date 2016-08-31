
"""
Timer data and state containers (hidden from user).
"""

from timeit import default_timer as timer
import copy


class Timer(object):
    """ Current (temporary) values describing state of timer.
    (Disappears or irrelevant after timing is complete.)
    """

    def __init__(self,
                 name,
                 rgstr_stamps=list(),
                 save_itrs=True,
                 dump=None,
                 named_loop=False,
                 in_loop=False,
                 **kwargs):
        self.name = str(name)
        self.rgstr_stamps = rgstr_stamps
        self.save_itrs = bool(save_itrs)
        self.dump = dump  # refers to a Times instance
        self.named_loop = named_loop  # needed for restoring dump after deepcopy
        self.in_loop = bool(in_loop)
        self.times = None
        self.user_subdivision = False
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


class Times(object):
    """ Timing data resides here, including tree structure.
    (Survives after timing is complete).
    """

    def __init__(self, name=None, parent=None, pos_in_parent=None):
        self.name = None if name is None else str(name)
        self.parent = parent  # refer to another Times instance.
        self.pos_in_parent = pos_in_parent  # refers to a stamp name.
        self.reset()

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        new.stamps = copy.deepcopy(self.stamps, memo)
        new.subdvsn = copy.deepcopy(new.subdvsn, memo)
        new.par_subdvsn = copy.deepcopy(self.par_subdvsn, memo)
        # Avoid deepcopy of parent, and update that attribute.
        for _, sub_list in new.subdvsn.iteritems():
            for sub in sub_list:
                sub.parent = new
        for _, par_dict in new.par_subdvsn.iteritems():
            for _, par_list in par_dict.iteritems():
                for sub in par_list:
                    sub.parent = new
        return new

    def reset(self):
        self.stamps = Stamps()
        self.total = 0.
        self.stamps_sum = 0.
        self.self_agg = 0.
        self.subdvsn = dict()
        self.par_subdvsn = dict()
        self.par_in_parent = False


class Stamps(object):
    """ Detailed timing breakdown resides here."""
    def __init__(self):
        self.cum = dict()
        self.itrs = dict()
        self.itr_num = dict()
        self.itr_max = dict()
        self.itr_min = dict()
        self.order = list()
