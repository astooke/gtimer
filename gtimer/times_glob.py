
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
    g.rf.self_agg += g.tf.self_cut  # (now add self_cut including self time of stop())
    if g.tf.dump is not None:
        t = timer()
        times_loc.merge_times(g.tf.dump, g.rf, stamps_as_itr=g.tf.save_itrs)
        g.tf.dump.parent.self_agg += timer() - t + g.rf.self_agg
    elif g.rf.parent is not None:
        g.rf.parent.self_agg += g.rf.self_agg


def assign_subdivisions(position):
    new_pos = position not in g.rf.subdivisions and g.tf.subdivisions_awaiting
    if new_pos:
        g.rf.subdivisions[position] = list()
        for _, sub_times in g.tf.subdivisions_awaiting.iteritems():
            sub_times.pos_in_parent = position
            g.rf.subdivisions[position] += [sub_times]
    else:
        for _, sub_times in g.tf.subdivisions_awaiting.iteritems():
            is_prev_sub = False
            for old_sub in g.rf.subdivisions[position]:
                if old_sub.name == sub_times.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                times_loc.merge_times(old_sub, sub_times, stamps_as_itrs=g.tf.save_itrs)
            else:
                sub_times.pos_in_parent = position
                g.rf.subdivisions[position].append(sub_times)
    g.tf.subdivisions_awaiting.clear()


def par_assign_subdivisions(position):
    new_pos = position not in g.rf.par_subdivisions and g.tf.subdivisions_awaiting
    if new_pos:
        for par_name, sub_list in g.tf.subdivisions_awaiting:
            for sub_times in sub_list:
                sub_times.pos_in_parent = position
        g.rf.par_subdivisions[position] = g.tf.subdivisions_awaiting
    else:
        for par_name, sub_list in g.tf.subdivisions_awaiting:
            if par_name not in g.rf.par_subdivisions[position]:
                for sub_times in sub_list:
                    sub_times.pos_in_parent = position
                g.rf.par_subdivisions[position][par_name] = sub_list
            else:
                for sub_times in sub_list:
                    is_prev_sub = False
                    for old_sub in g.rf.subdivisions[position][par_name]:
                        if old_sub.name == sub_times.name:
                            is_prev_sub = True
                            break
                    if is_prev_sub:
                        times_loc.merge_times(old_sub, sub_times, stamps_as_itrs=g.tf.save_itrs)
                    else:
                        sub_times.pos_in_parent = position
                        g.rf.subdivisions[position][par_name].append(sub_times)
    g.tf.par_subdivisions_awaiting.clear()
