
"""
Times() functions acting on global variables (hidden from user).
"""

from timeit import default_timer as timer
import data_glob as g
import times_loc


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
    for s, val in g.sf.cum.iteritems():
        # (for saving stamps_as_itr)
        if s not in g.sf.itr_num:
            g.sf.itr_num[s] = 1
            g.sf.itr_max[s] = val
            g.sf.itr_min[s] = val
    if g.tf.dump is not None:
        t = timer()
        times_loc.merge_times(g.tf.dump, g.rf, stamps_as_itr=g.tf.save_itrs)
        g.tf.dump.parent.self_agg += timer() - t + g.rf.self_agg
    elif g.rf.parent is not None:
        g.rf.parent.self_agg += g.rf.self_agg


def assign_subdivisions(position):
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
                times_loc.merge_times(old_sub, sub_times, stamps_as_itrs=g.tf.save_itrs)
            else:
                sub_times.pos_in_parent = position
                g.rf.subdvsn[position].append(sub_times)
    g.tf.subdvsn_awaiting.clear()


def assign_par_subdivisions(position):
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
                        times_loc.merge_times(old_sub, sub_times, stamps_as_itrs=g.tf.save_itrs)
                    else:
                        sub_times.pos_in_parent = position
                        g.rf.par_subdvsn[position][par_name].append(sub_times)
    g.tf.par_subdvsn_awaiting.clear()
