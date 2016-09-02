
"""
Times() functions acting on global variables (hidden from user).
"""

from timeit import default_timer as timer

from gtimer.private import glob as g
from gtimer.local import merge


#
# Functions to expose elsewhere in the package.
#


def dump_times():
    g.rf.total = g.tf.tmp_total - g.rf.self_agg  # (have already subtracted self_cut)
    g.rf.stamps_sum = sum([v for _, v in g.sf.cum.iteritems()])
    g.rf.self_agg += g.tf.self_cut  # (now add self_cut including self time of stop())
    if g.sf.itrs:
        for s, itr_list in g.sf.itrs.iteritems():
            g.sf.itr_max[s] = max(itr_list)
            nonzero_itrs = filter(lambda x: x > 0., itr_list)
            g.sf.itr_num[s] = len(nonzero_itrs)
            if g.sf.itr_num[s] > 0:
                g.sf.itr_min[s] = min(nonzero_itrs)
            else:
                g.sf.itr_min[s] = 0.
    for s, val in g.sf.cum.iteritems():  # (for saving stamps_as_itr)
        if s not in g.sf.itr_num:
            g.sf.itr_num[s] = 1
            g.sf.itr_max[s] = val
            g.sf.itr_min[s] = val
    if g.tf.dump is not None:
        t = timer()
        merge.merge_times(g.tf.dump, g.rf)
        g.tf.dump.parent.self_agg += timer() - t + g.rf.self_agg
    elif g.rf.parent is not None:
        g.rf.parent.self_agg += g.rf.self_agg


def assign_subdivisions(position, keep_subdivisions=True):
    if keep_subdivisions:
        if g.tf.subdsvn_awaiting:
            _assign_subdvsn(position)
        if g.tf.par_subdvsn_awaiting:
            _assign_par_subdvsn(position)
    g.tf.subdvsn_awaiting.clear()
    g.tf.par_subdvsn_awaiting.clear()


#
# Private helper functions.
#


def _assign_subdvsn(position):
    new_pos = position not in g.rf.subdvsn and g.tf.subdvsn_awaiting
    if new_pos:
        g.rf.subdvsn[position] = list()
        for _, sub_times in g.tf.subdvsn_awaiting.iteritems():
            sub_times.pos_in_parent = position
            g.rf.subdvsn[position] += [sub_times]
    else:
        for _, sub_times in g.tf.subdvsn_awaiting.iteritems():
            is_prev_sub = False
            for old_sub in g.rf.subdvsn[position]:
                if old_sub.name == sub_times.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                merge.merge_times(old_sub, sub_times)
            else:
                sub_times.pos_in_parent = position
                g.rf.subdvsn[position].append(sub_times)


def _assign_par_subdvsn(position):
    new_pos = position not in g.rf.par_subdvsn and g.tf.par_subdvsn_awaiting
    if new_pos:
        g.rf.par_subdvsn[position] = dict()
        for par_name, sub_list in g.tf.par_subdvsn_awaiting.iteritems():
            for sub_times in sub_list:
                sub_times.pos_in_parent = position
            g.rf.par_subdvsn[position][par_name] = sub_list
    else:
        for par_name, sub_list in g.tf.par_subdvsn_awaiting.iteritems():
            if par_name not in g.rf.par_subdvsn[position]:
                for sub_times in sub_list:
                    sub_times.pos_in_parent = position
                g.rf.par_subdvsn[position][par_name] = sub_list
            else:
                for sub_times in sub_list:
                    is_prev_sub = False
                    for old_sub in g.rf.par_subdvsn[position][par_name]:
                        if old_sub.name == sub_times.name:
                            is_prev_sub = True
                            break
                    if is_prev_sub:
                        merge.merge_times(old_sub, sub_times)
                    else:
                        sub_times.pos_in_parent = position
                        g.rf.par_subdvsn[position][par_name].append(sub_times)
