
"""
Internal, global data holding timer hierarchy and state.  Provides shortcut
references to the timer and loop currently in "focus".
"""
from __future__ import absolute_import

from gtimer.local.stack import Stack
from gtimer.local.timer import Timer
from gtimer.local.loop import Loop


#
# Containers for management of timer hierarchy.
#
timer_stack = None
loop_stack = None


#
# Shortcut variables.
#
root = None  # base of timer stack
t = None  # active end of timer stack: 'Timer in Focus'
r = None  # t.times: 'Times (Record) in Focus'
s = None  # t.times.stamps: 'Stamps in Focus'
tm1 = None  # second from the top of timer stack 't minus 1' (used in named loops)
rm1 = None
sm1 = None
lp = None  # loop_stack.focus: 'Loop in Focus'


#
# Shortcut functions.
#


def create_next_timer(*args, **kwargs):
    global t, r, s, tm1, rm1, sm1
    t, tm1 = timer_stack.create_next(*args, **kwargs)
    r = None if t is None else t.times
    s = None if r is None else r.stamps
    rm1 = None if tm1 is None else tm1.times
    sm1 = None if rm1 is None else rm1.stamps
    return t


def remove_last_timer():
    global t, r, s, tm1, rm1, sm1
    t, tm1 = timer_stack.remove_last()
    r = None if t is None else t.times
    s = None if r is None else r.stamps
    rm1 = None if tm1 is None else tm1.times
    sm1 = None if rm1 is None else rm1.stamps


def create_next_loop(*args, **kwargs):
    global lp
    lp, _ = loop_stack.create_next(*args, **kwargs)


def remove_last_loop():
    global lp
    lp, _ = loop_stack.remove_last()


def refresh_shortcuts():
    global t, r, s, tm1, rm1, sm1, lp
    t, tm1 = timer_stack.stack_return()
    r = None if t is None else t.times
    s = None if r is None else r.stamps
    rm1 = None if tm1 is None else tm1.times
    sm1 = None if rm1 is None else rm1.stamps
    lp, _ = loop_stack.stack_return()


#
# Initialization.
#

def hard_reset():
    global timer_stack, loop_stack, root, lp
    timer_stack = Stack(Timer)
    loop_stack = Stack(Loop)
    root = create_next_timer('root')  # (this refreshes shortcuts)
    lp = None


hard_reset()


#
# Other helpers.
#

def get_current_timer():
    global t
    return t
