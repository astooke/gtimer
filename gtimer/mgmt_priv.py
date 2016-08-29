
"""
Timer management functions to hide from user but expose
elsewhere in package.
"""

import data_glob as g
import mgmt_pub
import timer_glob


def subdivide_named_loop(name, rgstr_stamps, save_itrs):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.rf.subdivisions:
        assert len(g.rf.subdivisions[name]) == 1
        dump = g.rf.subdivisions[name][0]
        g.create_next_timer(name, rgstr_stamps, save_itrs, in_loop=True)
        g.tf.dump = dump
    else:
        # No previous, write directly to assigned subdivision in parent times.
        g.create_next_timer(name, rgstr_stamps, save_itrs, in_loop=True, parent=g.rf, pos_in_parent=name)
        new_times = g.rf
        g.focus_backward_timer()
        g.rf.subdivisions[name] = [new_times]
        g.focus_forward_timer()


def sanitize_rgstr_stamps(rgstr_stamps):
    if not isinstance(rgstr_stamps, (list, tuple)):
        raise TypeError("Expected list or tuple for rgstr_stamps (elements passed through str()).")
    rgstr_stamps = list(rgstr_stamps)
    for s in rgstr_stamps:
        s = str(s)
    return rgstr_stamps


def subdivide(*args, **kwargs):
    """ To be called internally instead of public version."""
    mgmt_pub.subdivide(*args, **kwargs)
    g.tf.user_subdivision = False  # Protect from user closure.


def end_subdivision():
    """ To be called internally instead of public version."""
    if g.tf.user_subdivision:
        raise RuntimeError("gtimer attempted to end user-generated subdivision.")
    assert not g.tf.in_loop, "gtimer attempted to close subidivision while in timed loop."
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()
