
"""
Functions for creating new timers, closing old ones, and handling the
relationships of the timers. (Mostly exposed to user.)
"""

import data_glob as g
import timer_glob


__all__ = ['open_next_timer', 'close_last_timer', 'wrap', 'rename_root_timer']


#
# Expose to user
#


def open_next_timer(name, rgstr_stamps=list()):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    if name in g.tf.children_awaiting:
        # Previous dump exists.
        # (e.g. multiple calls of same wrapped function between stamps)
        dump = g.tf.children_awaiting[name]
        g.create_next_timer(name, rgstr_stamps)
        g.tf.dump = dump
    else:
        # No previous, write directly to awaiting child in parent times.
        g.create_next_timer(name, rgstr_stamps, parent=g.rf)
        new_times = g.rf
        g.focus_backward_timer()
        g.tf.children_awaiting[name] = new_times
        g.focus_forward_timer()


def close_last_timer():
    if g.tf is g.root_timer:
        raise RuntimeError('Attempted to close root timer, can only stop it.')
    if not g.tf.stopped:
        timer_glob.stop()
    g.remove_last_timer()


def wrap(func, rgstr_stamps=list()):
    name = func.__name__
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)

    def timer_wrapped(*args, **kwargs):
        open_next_timer(name, rgstr_stamps)
        result = func(*args, **kwargs)
        close_last_timer()
        return result
    return timer_wrapped


def rename_root_timer(name):
    name = str(name)
    g.focus_root_timer()
    g.tf.name = name
    g.focus_last_timer()


#
# Hide from user but expose elswhere in package.
#

def open_named_loop_timer(name, rgstr_stamps):
    name = str(name)
    rgstr_stamps = sanitize_rgstr_stamps(rgstr_stamps)
    if name in g.rf.children:
        assert len(g.rf.children[name]) == 1  # There should only be one child.
        dump = g.rf.children[name][0]
        g.create_next_timer(name, rgstr_stamps, loop_depth=1)
        g.tf.dump = dump
    else:
        # No previous, write directly to assigned child in parent times.
        g.create_next_timer(name, rgstr_stamps, loop_depth=1, parent=g.rf, pos_in_parent=name)
        new_times = g.rf
        g.focus_backward_timer()
        g.rf.children[name] = [new_times]
        g.focus_forward_timer()


def sanitize_rgstr_stamps(rgstr_stamps):
    if not isinstance(rgstr_stamps, (list, tuple)):
        raise TypeError("Expected list or tuple for rgstr_stamps (entries converted with str()).")
    rgstr_stamps = list(rgstr_stamps)
    for s in rgstr_stamps:
        s = str(s)
    return rgstr_stamps
