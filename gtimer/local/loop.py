

class Loop(object):
    """Hold info for name checking and assigning."""

    def __init__(self, name=None, rgstr_stamps=list(), save_itrs=True):
        self.name = None if name is None else str(name)
        self.stamps = list()
        self.rgstr_stamps = rgstr_stamps
        self.itr_stamp_used = dict()
        self.save_itrs = save_itrs
        self.itr_stamps = dict()
        self.first_itr = True