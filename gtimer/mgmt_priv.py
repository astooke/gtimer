
"""
Timer management functions to hide from user but expose
elsewhere in package.
"""

import data_glob as g


def open_named_loop_timer(name, rgstr_stamps, save_itrs):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.rf.children:
        assert len(g.rf.children[name]) == 1  # There should only be one child.
        dump = g.rf.children[name][0]
        g.create_next_timer(name, rgstr_stamps, save_itrs, in_loop=True)
        g.tf.dump = dump
    else:
        # No previous, write directly to assigned child in parent times.
        g.create_next_timer(name, rgstr_stamps, save_itrs, in_loop=True, parent=g.rf, pos_in_parent=name)
        new_times = g.rf
        g.focus_backward_timer()
        g.rf.children[name] = [new_times]
        g.focus_forward_timer()


def sanitize_rgstr_stamps(rgstr_stamps):
    if not isinstance(rgstr_stamps, (list, tuple)):
        raise TypeError("Expected list or tuple for rgstr_stamps (elements passed through str()).")
    rgstr_stamps = list(rgstr_stamps)
    for s in rgstr_stamps:
        s = str(s)
    return rgstr_stamps
