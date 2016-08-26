
"""
Times() functions acting on locally provided variables (hidden from user).
"""

#
# Function to expose elsewhere in the package.
#


def merge_times(rcvr, new, stamps_as_itr=True, agg_up=True):
    rcvr.total += new.total
    rcvr.self_cut += new.self_cut
    if agg_up:
        aggregate_up_self(rcvr, new.self_agg)
    else:
        rcvr.self_agg += new.self_agg
    if stamps_as_itr:
        _merge_stamps_as_itr(rcvr, new)
    _merge_stamps(rcvr, new)
    _merge_children(rcvr, new)


def aggregate_up_self(times, val):
    times.self_agg += val
    if times.parent is not None:
        aggregate_up_self(times.parent, val)


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


def _merge_children(rcvr, new):
    for child_pos, new_children in new.children.iteritems():
        if child_pos in rcvr.children:
            for new_child in new_children:
                for rcvr_child in rcvr.children[child_pos]:
                    if rcvr_child.name == new_child.name:
                        merge_times(rcvr_child, new_child, agg_up=False)
                        # merge_children(rcvr_child, new_child)
                        break
                else:
                    new_child.parent = rcvr
                    rcvr.children[child_pos] += [new_child]
        else:
            for child in new_children:
                child.parent = rcvr
            rcvr.children[child_pos] = new_children
    # Clean up references to old data as we go (not sure if helpful?).
    new.children.clear()


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
