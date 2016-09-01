
"""
Times() functions acting on locally provided variables.
(So far, hidden from user)...might expose some
to support multiprocessing, if user has to manipulate
saved Times objects.
"""

#
# Function to expose elsewhere in the package.
#


def merge_times(rcvr, new):
    rcvr.total += new.total
    rcvr.stamps_sum += new.stamps_sum
    rcvr.self_agg += new.self_agg
    _merge_stamps(rcvr, new)
    _merge_subdivisions(rcvr, new)
    _merge_par_subdivisions(rcvr, new)


#
# Private, helper functions.
#


def _merge_stamps(rcvr, new):
    save_itrs = rcvr.save_itrs
    rcvr = rcvr.stamps
    new = new.stamps
    for s in new.order:
        if s not in rcvr.order:
            rcvr.order.append(s)
    if save_itrs:
        _stamps_as_itr(rcvr, new)  # do this before cum
    _merge_dict(rcvr, new, 'itrs')  # (in any case, maybe loop with save_itrs)
    _merge_dict(rcvr, new, 'cum')
    _merge_dict(rcvr, new, 'itr_num')
    _merge_dict_itr(rcvr, new, 'itr_max', max)
    _merge_dict_itr(rcvr, new, 'itr_min', min)


def _merge_dict(rcvr, new, attr):
    rcvr_dict = getattr(rcvr, attr)
    new_dict = getattr(new, attr)
    for k, v in new_dict.iteritems():
        if k in rcvr_dict:
            rcvr_dict[k] += v
        else:
            rcvr_dict[k] = v


def _merge_dict_itr(rcvr, new, attr, itr_func):
    rcvr_dict = getattr(rcvr, attr)
    new_dict = getattr(new, attr)
    for k, v in new_dict.iteritems():
        if k in rcvr_dict:
            rcvr_dict[k] = itr_func(v, rcvr_dict[k])
        else:
            rcvr_dict[k] = v


def _stamps_as_itr(rcvr, new):
    for k, v in new.cum.iteritems():
        if new.itr_num[k] == 1:  # (then it won't be in new.itrs)
            if k in rcvr.itrs:
                rcvr.itrs[k].append(v)
            elif k in rcvr.cum:
                rcvr.itrs[k] = [rcvr.cum[k], v]


def _merge_subdivisions(rcvr, new):
    for sub_pos, new_sub_list in new.subdvsn.iteritems():
        if sub_pos in rcvr.subdvsn:
            add_list = []  # to avoid writing to loop iterate
            for new_sub in new_sub_list:
                for rcvr_sub in rcvr.subdvsn[sub_pos]:
                    if rcvr_sub.name == new_sub.name:
                        merge_times(rcvr_sub, new_sub)
                        break
                else:
                    new_sub.parent = rcvr
                    add_list.append(new_sub)
            rcvr.subdvsn[sub_pos] += add_list
        else:
            for sub in new_sub_list:
                sub.parent = rcvr
            rcvr.subdvsn[sub_pos] = new_sub_list
    # Clean up references to old data as we go (not sure if helpful?).
    new.subdvsn.clear()


def _merge_par_subdivisions(rcvr, new):
    for sub_pos, par_dict in new.par_subdvsn.iteritems():
        if sub_pos in rcvr.par_subdvsn:
            for par_name, new_list in par_dict.iteritems():
                if par_name in rcvr.par_subdvsn[sub_pos]:
                    rcvr_list = rcvr.par_subdvsn[sub_pos][par_name]
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
                    rcvr.par_subdvsn[sub_pos][par_name] += add_list
                else:
                    for new_sub in new_list:
                        new_sub.parent = rcvr
                        new_sub.par_in_parent = True
                    rcvr.par_subdvsn[sub_pos][par_name] = new_list
        else:
            for par_name, par_list in par_dict.iteritems():
                for new_sub in par_list:
                    new_sub.parent = rcvr
                    new_sub.par_in_parent = True
            rcvr.par_subdvsn[sub_pos] = par_dict
    new.par_subdvsn.clear()
