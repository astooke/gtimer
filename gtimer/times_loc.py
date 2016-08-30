
"""
Times() functions acting on locally provided variables.
(So far, hidden from user)...might expose some
to support multiprocessing, if user has to manipulate
saved Times objects.
"""

#
# Function to expose elsewhere in the package.
#


def merge_times(rcvr, new, stamps_as_itr=True):
    rcvr.total += new.total
    rcvr.stamps_sum += new.stamps_sum
    rcvr.self_agg += new.self_agg
    if stamps_as_itr:
        _merge_stamps_as_itr(rcvr, new)
    _merge_stamps(rcvr, new)
    _merge_subdivisions(rcvr, new)
    _merge_par_subdivisions(rcvr, new)


#
# Private, helper functions.
#


def _merge_stamps(rcvr, new):
    rcvr = rcvr.stamps
    new = new.stamps
    for s in new.order:
        if s not in rcvr.order:
            rcvr.order.append(s)
    _merge_dict(rcvr, new, 'cum')
    _merge_dict(rcvr, new, 'itrs')
    _merge_dict(rcvr, new, 'num_itrs')


def _merge_subdivisions(rcvr, new):
    for sub_pos, new_subdivisions in new.subdivisions.iteritems():
        if sub_pos in rcvr.subdivisions:
            add_list = []  # to avoid writing to loop iterate
            for new_sub in new_subdivisions:
                for rcvr_sub in rcvr.subdivisions[sub_pos]:
                    if rcvr_sub.name == new_sub.name:
                        merge_times(rcvr_sub, new_sub)
                        break
                else:
                    new_sub.parent = rcvr
                    add_list.append(new_sub)
            rcvr.subdivisions[sub_pos] += add_list
        else:
            for sub in new_subdivisions:
                sub.parent = rcvr
            rcvr.subdivisions[sub_pos] = new_subdivisions
    # Clean up references to old data as we go (not sure if helpful?).
    new.subdivisions.clear()


def _merge_par_subdivisions(rcvr, new):
    for sub_pos, par_dict in new.par_subdivisions.iteritems():
        if sub_pos in rcvr.par_subdivisions:
            for par_name, new_list in par_dict.iteritems():
                if par_name in rcvr.par_subdivisions[sub_pos]:
                    rcvr_list = rcvr.par_subdivisions[sub_pos][par_name]
                    add_list = []  # to avoid writing to loop iterate
                    for new_sub in new_list:
                        for rcvr_sub in rcvr_list:
                            if rcvr_sub.name == new_sub.name:
                                merge_times(rcvr_sub, new_sub)
                                break
                        else:
                            new_sub.parent = rcvr
                            new_sub.par_in_parent = True
                            add_list.append(new_sub)
                    rcvr.par_subdivisions[sub_pos][par_name] += add_list
                else:
                    for new_sub in new_list:
                        new_sub.parent = rcvr
                        new_sub.par_in_parent = True
                    rcvr.par_subdivisions[sub_pos][par_name] = new_list
        else:
            for par_name, par_list in par_dict.iteritems():
                for new_sub in par_list:
                    new_sub.parent = rcvr
                    new_sub.par_in_parent = True
            rcvr.par_subdivisions[sub_pos] = par_dict
    new.par_subdivisions.clear()


def _merge_dict(rcvr, new, attr):
    rcvr_dict = getattr(rcvr, attr)
    new_dict = getattr(new, attr)
    for k, v in new_dict.iteritems():
        if k in rcvr_dict:
            rcvr_dict[k] += v
        else:
            rcvr_dict[k] = v


def _merge_stamps_as_itr(rcvr, new):
    rcvr = rcvr.stamps
    new = new.stamps
    for k, v in new.cum.iteritems():
        if k not in new.itrs:
            if k in rcvr.itrs:
                rcvr.itrs[k].append(v)
                rcvr.num_itrs[k] += 1
            else:
                if k in rcvr.cum:
                    rcvr.itrs[k] = [rcvr.cum[k], v]
                    rcvr.num_itrs[k] = 2
                else:
                    rcvr.itrs[k] = [v]
                    rcvr.num_itrs[k] = 1
    for k in rcvr.cum:
        if k not in new.cum:
            if k in rcvr.itrs:
                rcvr.itrs[k].append(0.)
            else:
                rcvr.itrs[k] = [rcvr.cum[k], 0.]
                rcvr.num_itrs[k] = 1
