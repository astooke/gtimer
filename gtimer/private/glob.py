
"""
All global data and timer state information resides here.
(Hidden from user.)
"""

from gtimer.local.stack import Stack
from gtimer.local.timer import Timer
from gtimer.local.loop import Loop


#
# Constants.
#
UNASGN = 'UNASSIGNED'


#
# Containers for management of timer hierarchy.
#
timer_stack = None
loop_stack = None


#
# Shortcut variables.
#
tf = None  # top of timer stack: 'Timer in Focus'
rf = None  # tf.times: 'Times (Record) in Focus'
sf = None  # tf.times.stamps: 'Stamps in Focus'
tfmin1 = None  # second from the top of timer stack 'tf minus 1' (for named loops)
rfmin1 = None
sfmin1 = None
lf = None  # loop_stack.focus: 'Loop in Focus'


#
# Shortcut functions.
#


def create_next_timer(*args, **kwargs):
    global tf, rf, sf, tfmin1, rfmin1, sfmin1
    tf, tfmin1 = timer_stack.create_next(*args, **kwargs)
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps
    rfmin1 = None if tfmin1 is None else tfmin1.times
    sfmin1 = None if rfmin1 is None else rfmin1.stamps
    return tf


def remove_last_timer():
    global tf, rf, sf, tfmin1, rfmin1, sfmin1
    tf, tfmin1 = timer_stack.remove_last()
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps
    rfmin1 = None if tfmin1 is None else tfmin1.times
    sfmin1 = None if rfmin1 is None else rfmin1.stamps


def create_next_loop(*args, **kwargs):
    global lf
    lf, _ = loop_stack.create_next(*args, **kwargs)


def remove_last_loop():
    global lf
    lf, _ = loop_stack.remove_last()


def refresh_shortcuts():
    global tf, rf, sf, tfmin1, rfmin1, sfmin1, lf
    tf, tfmin1 = timer_stack.stack_return()
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps
    rfmin1 = None if tfmin1 is None else tfmin1.times
    sfmin1 = None if rfmin1 is None else rfmin1.stamps
    lf, _ = loop_stack.stack_return()


#
# Initialization.
#

def hard_reset():
    global timer_stack, loop_stack, root_timer, lf
    timer_stack = Stack(Timer)
    loop_stack = Stack(Loop)
    root_timer = create_next_timer('root')
    lf = None


hard_reset()
