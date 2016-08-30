
"""
Timer management functions to hide from user but expose
elsewhere in package.
"""

import data_glob as g
import mgmt_pub
import timer_glob
import loop
import copy


def subdivide_named_loop(name, rgstr_stamps, save_itrs):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    save_itrs = bool(save_itrs)
    if name in g.rf.subdivisions:
        assert len(g.rf.subdivisions[name]) == 1
        dump = g.rf.subdivisions[name][0]
        g.create_next_timer(name,
                            rgstr_stamps,
                            save_itrs,
                            named_loop=True,
                            in_loop=True)
        g.tf.dump = dump
    else:
        # No previous, write directly to assigned subdivision in parent times.
        g.create_next_timer(name,
                            rgstr_stamps,
                            save_itrs,
                            named_loop=True,
                            in_loop=True,
                            parent=g.rf,
                            pos_in_parent=name)
        g.tfmin1.times.subdivisions[name] = [g.rf]


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


def collapse_subdivision():
    if g.tf.in_loop:
        loop.loop_end(end_stamp_unique=False)
        loop.exit_loop()
    else:
        timer_glob.stop()
        g.remove_last_timer()


def copy_timer_stack():
    stack_copy = copy.deepcopy(g.timer_stack)
    # Update/synchronize the dump relationships.
    for i in range(1, len(g.timer_stack)):
        name = stack_copy[i].name
        if g.timer_stack[i].dump is None:
            if stack_copy[i].named_loop:
                stack_copy[i - 1].times.subdivisions[name] = [stack_copy[i].times]
            else:
                stack_copy[i - 1].subdivisions_awaiting[name] = stack_copy[i].times
        else:
            if stack_copy[i].named_loop:
                stack_copy[i].dump = stack_copy[i - 1].times.subdivisions[name]
            else:
                stack_copy[i].dump = stack_copy[i - 1].subdivisions_awaiting[name]
    return stack_copy


def collapse_times():
    """Make copies of everything, assign to globals so functions work on them,
    extract the times, then restore the running stacks.
    """
    original_timer_stack = g.timer_stack
    original_loop_stack = g.loop_stack
    timer_stack_copy = copy_timer_stack()
    loop_stack_copy = copy.deepcopy(g.loop_stack)
    g.timer_stack = timer_stack_copy
    g.loop_stack = loop_stack_copy
    g.refresh_shortcuts()
    while len(g.timer_stack) > 1:
        collapse_subdivision()
    timer_glob.stop()
    collapsed_times = g.rf
    g.timer_stack = original_timer_stack  # (loops throw error if not same object!)
    g.loop_stack = original_loop_stack
    g.refresh_shortcuts()
    return collapsed_times
