
"""
All global data and timer state information resides here.
(Hidden from user.)
"""

from focusedstack import FocusedStack
from timer_classes import Timer
from loop import Loop


#
# Constants.
#
UNASGN = 'UNASSIGNED'


#
# Containers for management of timer creation/destruction.
#
timer_stack = FocusedStack(Timer)
loop_stack = FocusedStack(Loop)


#
# Shortcut variables.
#
tf = None  # timer_stack.focus: 'Timer in Focus'
rf = None  # timer_stack.focus.times: 'Times (Record) in Focus'
sf = None  # timer_stack.focus.times.stamps: 'Stamps in Focus'
lf = None  # loop_stack.focus: 'Loop in Focus'


# TO DO: Automate the making of these shortcuts.
#
# def focus_shortcut_builder(focus_var, append_name, heap, method, *args, **kwargs):
#     def shortcut(*args, **kwargs):
#         heap.method(*args, **kwargs)
#         global focus_var
#         focus_var = heap.focus
#     shortcut.__name__ = method.__name__ + append_name
#     return shortcut
#

#
# Shortcut functions.
#

def create_next_timer(name, *args, **kwargs):
    global tf, rf, sf
    tf = timer_stack.create_next(name, *args, **kwargs)
    rf = tf.times
    sf = rf.stamps


def remove_last_timer():
    global tf, rf, sf
    tf = timer_stack.remove_last()
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None


def pop_last_timer():
    global tf, rf, sf
    last_timer = timer_stack.pop_last()
    tf = timer_stack.focus
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None
    return last_timer


def focus_backward_timer():
    global tf, rf, sf
    tf = timer_stack.focus_backward()
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None


def focus_forward_timer():
    global tf, rf, sf
    tf = timer_stack.focus_forward()
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None


def focus_last_timer():
    global tf, rf, sf
    tf = timer_stack.focus_last()
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None


def focus_root_timer():
    global tf, rf, sf
    tf = timer_stack.focus_root()
    if tf is not None:
        rf = tf.times
        sf = rf.stamps
    else:
        rf = None
        sf = None


def create_next_loop(*args, **kwargs):
    global lf
    print "creating loop"
    lf = loop_stack.create_next(*args, **kwargs)


def remove_last_loop():
    global lf
    lf = loop_stack.remove_last()


def focus_backward_loop():
    global lf
    lf = loop_stack.focus_backward()


def focus_forward_loop():
    global lf
    lf = loop_stack.focus_forward()


def focus_last_loop():
    global lf
    lf = loop_stack.focus_last()


def focus_root_loop():
    global lf
    lf = loop_stack.focus_root()


#
# Initialization.
#
create_next_timer('root')  # (user may not remove this one)
root_timer = tf
