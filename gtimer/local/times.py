
import copy


class Times(object):
    """ Timing data resides here, including tree structure.
    (Survives after timing is complete).
    """

    def __init__(self, 
                 name=None, 
                 parent=None, 
                 pos_in_parent=None,
                 save_itrs=True):
        self.name = None if name is None else str(name)
        self.parent = parent  # refer to another Times instance.
        self.pos_in_parent = pos_in_parent  # refers to a stamp name.
        self.save_itrs = save_itrs
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
