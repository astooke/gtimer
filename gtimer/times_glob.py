
"""
Times() functions acting on global variables (hidden from user).
"""

import data_glob as g
import times_loc


#
# Functions to expose elsewhere in the package.
#


def assign_children(position):
    new_pos = position not in g.rf.children and g.tf.children_awaiting
    for _, child_times in g.tf.children_awaiting.iteritems():
        times_loc.aggregate_up_self(g.rf, child_times.self_agg)
        child_times.pos_in_parent = position  # (Not needed for merge case but OK.)
    if new_pos:
        g.rf.children[position] = list()
        for _, child_times in g.tf.children_awaiting.iteritems():
            g.rf.children[position] += [child_times]
    else:
        for _, child_times in g.tf.children_awaiting.iteritems():
            is_prev_child = False
            for old_child in g.rf.children[position]:
                if old_child.name == child_times.name:
                    is_prev_child = True
                    break
            if is_prev_child:
                times_loc.merge_times(old_child, child_times, stamps_as_itrs=g.tf.save_itrs)
            else:
                g.rf.children[position].append(child_times)
    g.tf.children_awaiting.clear()


def dump_times():
    if g.tf.dump is not None:
        times_loc.merge_times(g.tf.dump, g.rf, stamps_as_itr=g.tf.save_itrs)


def par_assign_children(position):
    new_pos = position not in g.rf.par_children and g.tf.children_awaiting
    for par_name, child_list in g.tf.children_awaiting:
        max_self_agg = max([times.self_agg for times in child_list])
        times_loc.aggregate_up_self(g.rf, max_self_agg)
        for child in child_list:
            child.pos_in_parent = position
    if new_pos:
        g.rf.par_children[position] = g.tf.children_awaiting
    else:
        for par_name, child_list in g.tf.children_awaiting:
            if par_name not in g.rf.par_children[position]:
                g.rf.par_children[position][par_name] = child_list
            else:
                for child_times in child_list:
                    is_prev_child = False
                    for old_child in g.rf.children[position][par_name]:
                        if old_child.name == child_times.name:
                            is_prev_child = True
                            break
                    if is_prev_child:
                        times_loc.merge_times(old_child, child_times, stamps_as_itrs=g.tf.save_itrs)
                    else:
                        g.rf.children[position][par_name].append(child_times)
    g.tf.par_children_awaiting.clear()
