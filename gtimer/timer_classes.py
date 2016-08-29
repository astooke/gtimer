
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
                 in_loop=False,
                 **kwargs):
        self.name = str(name)
        self.rgstr_stamps = rgstr_stamps
        self.save_itrs = bool(save_itrs)
        self.dump = dump  # refers to a Times instance
        self.in_loop = bool(in_loop)
        self.times = None
        self.user_subdivision = False
        self.reset()
        self.times = Times(name, **kwargs)

    def reset(self):
        self.stopped = False
        self.paused = False
        self.tmp_total = 0.
        self.self_cut = 0.
        self.subdivisions_awaiting = dict()
        self.par_subdivisions_awaiting = dict()
        self.start_t = timer()
        self.last_t = self.start_t
        if self.times is not None:
            self.times.reset()


class Times(object):
    """ Timing data resides here, including tree structure.
    (Survives after timing is complete).
    """

    def __init__(self, name, parent=None, pos_in_parent=None):
        self.name = str(name)
        self.parent = parent  # refer to another Times instance.
        self.pos_in_parent = pos_in_parent  # refers to a stamp name.
        self.reset()

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        new.stamps = copy.deepcopy(self.stamps, memo)
        new.subdivisions = copy.deepcopy(self.subdivisions, memo)
        new.par_subdivisions = copy.deepcopy(self.par_subdivisions, memo)
        # Avoid deepcopy of parent, and update attribute.
        for _, sub_list in new.subdivisions:
            for sub in sub_list:
                sub.parent = self
        for _, list_of_sub_lists in new.par_subdivisions:
            for sub_list in list_of_sub_lists:
                for sub in sub_list:
                    sub.parent = self
        return new

    def reset(self):
        self.stamps = Stamps()
        self.total = 0.
        self.self_agg = 0.
        self.subdivisions = dict()
        self.par_subdivisions = dict()
        self.par_in_parent = False


class Stamps(object):
    """ Detailed timing breakdown resides here."""
    def __init__(self):
        self.cum = dict()
        self.itrs = dict()
        self.order = list()
        self.sum_t = 0.
