
"""
Times() functions acting on global variables (hidden from user).
"""

import data_glob as g
import times_loc


#
# Functions to expose elsewhere in the package.
#


def assign_children(position, simple=False):
    """ Can always execute with simple=False and get the right result."""
    if simple:
        for _, child_times in g.tf.children_awaiting.iteritems():
            times_loc.aggregate_up_self(g.rf, child_times.self_agg)
            child_times.pos_in_parent = position
            if position in g.rf.children:
                g.rf.children[position] += [child_times]
            else:
                g.rf.children[position] = [child_times]
    else:
        for _, child_times in g.tf.children_awaiting.iteritems():
            times_loc.aggregate_up_self(g.rf, child_times.self_agg)
            is_prev_child = False
            if position in g.rf.children:
                for old_child in g.rf.children[position]:
                    if old_child.name == child_times.name:
                        is_prev_child = True
                        break
                if is_prev_child:
                    times_loc.merge_times(old_child, child_times)
            else:
                g.rf.children[position] = []
            if not is_prev_child:
                child_times.pos_in_parent = position
                g.rf.children[position] += [child_times]
    g.tf.children_awaiting.clear()


def dump_times():
    if g.tf.dump is not None:
        times_loc.merge_times(g.tf.dump, g.rf, stamps_as_itr=g.tf.save_itrs)
