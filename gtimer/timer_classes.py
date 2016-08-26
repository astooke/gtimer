
"""
Timer data and state containers (hidden from user).
"""

from timeit import default_timer as timer


class Timer(object):
    """ Current (temporary) values describing state of timer.
    (Disappears or irrelevant after timing is complete.)
    """

    def __init__(self, name, rgstr_stamps=list(), loop_depth=0, **kwargs):
        self.name = str(name)
        self.times = Times(name, **kwargs)
        self.loop_depth = loop_depth
        self.stopped = False
        self.paused = False
        self.children_awaiting = dict()  # key: name of Timer, value: Times instance
        self.dump = None  # refers to a Times instance
        self.rgstr_stamps = rgstr_stamps
        self.start_t = timer()
        self.last_t = self.start_t


class Times(object):
    """ Timing data resides here, including tree structure.
    (Survives after timing is complete).
    """

    def __init__(self, name, parent=None, pos_in_parent=None):
        self.name = str(name)
        self.stamps = Stamps()
        self.total = 0.
        self.self_cut = 0.  # Self time from this timer.
        self.self_agg = 0.  # Self time including all children.
        self.parent = parent  # refer to another Times instance.
        self.pos_in_parent = pos_in_parent  # refers to a stamp name.
        self.children = dict()  # key: stamp, value: list of Times instances.


class Stamps(object):
    """ Detailed timing breakdown resides here."""
    def __init__(self):
        self.cum = dict()
        self.itrs = dict()
        self.order = list()
        self.sum_t = 0.


# class Loop(object):

#     def __init__(self, save_itrs=True):
#         self.name = None
#         self.save_itrs = save_itrs
#         self.reg_stamps = list()
#         self.stamp_used = dict()
#         self.start_t = timer()
#         self.while_condition = True


# class TmpData(object):

#     def __init__(self):
#         self.self_t = 0.
#         self.calls = 0.
#         self.times = timesclass.Times()


# class Timer(object):

#     def __init__(self, name, save_self_itrs=True, save_loop_itrs=True):
#         self.name = name
#         self.save_itrs = save_self_itrs
#         self.save_loop_itrs = save_loop_itrs
#         self.reg_stamps = list()
#         self.in_loop = False
#         self.active = True
#         self.paused = False
#         self.start_t = timer()
#         self.last_t = self.start_t
#         self.tmp = TmpData()
#         self.loop = None
