
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


#
# Shortcut functions.
#

def t_shortcut(bound_method):
    global tf, rf, sf

    def shortcut(*args, **kwargs):
        global tf, rf, sf
        tf = bound_method(*args, **kwargs)
        if tf is not None:
            rf = tf.times
            sf = rf.stamps
        else:
            rf = None
            sf = None
        return tf

    return shortcut


create_next_timer = t_shortcut(timer_stack.create_next)
remove_last_timer = t_shortcut(timer_stack.remove_last)
focus_backward_timer = t_shortcut(timer_stack.focus_backward)
focus_forward_timer = t_shortcut(timer_stack.focus_forward)
focus_root_timer = t_shortcut(timer_stack.focus_root)
focus_last_timer = t_shortcut(timer_stack.focus_last)


def create_next_loop(*args, **kwargs):
    global lf
    lf = loop_stack.create_next(*args, **kwargs)


def remove_last_loop():
    global lf
    lf = loop_stack.remove_last()


#
# Initialization.
#
root_timer = create_next_timer('root')  # (user may not remove this one)
