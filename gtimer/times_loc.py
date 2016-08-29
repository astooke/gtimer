
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
    rcvr.self_cut += new.self_cut
    rcvr.self_agg += new.self_agg
    if stamps_as_itr:
        _merge_stamps_as_itr(rcvr, new)
    _merge_stamps(rcvr, new)
    _merge_subdivisions(rcvr, new)


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
    rcvr.sum_t += new.sum_t


def _merge_subdivisions(rcvr, new):
    for sub_pos, new_subdivisions in new.subdivisions.iteritems():
        if sub_pos in rcvr.subdivisions:
            for new_sub in new_subdivisions:
                for rcvr_sub in rcvr.subdivisions[sub_pos]:
                    if rcvr_sub.name == new_sub.name:
                        merge_times(rcvr_sub, new_sub)
                        break
                else:
                    new_sub.parent = rcvr
                    rcvr.subdivisions[sub_pos] += [new_sub]
        else:
            for sub in new_subdivisions:
                sub.parent = rcvr
            rcvr.subdivisions[sub_pos] = new_subdivisions
    # Clean up references to old data as we go (not sure if helpful?).
    new.subdivisions.clear()


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
            else:
                if k in rcvr.cum:
                    rcvr.itrs[k] = [rcvr.cum[k], v]
                else:
                    rcvr.itrs[k] = [v]
    for k in rcvr.cum:
        if k not in new.cum:
            if k in rcvr.itrs:
                rcvr.itrs[k].append(0.)
            else:
                rcvr.itrs[k] = [rcvr.cum[k], 0.]


# Man, I had just gotten around this incessant merging by having statically
# defined timers, who would accumulate their own data and could be connected
# by linking without having to move any data recursively. Now, with dynamic
# timers, back to having to merge trees (move data recursively) on the fly.
