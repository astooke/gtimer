
"""
All global data and timer state information resides here.
(Hidden from user.)
"""

from timer_classes import Timer
from loop import Loop


#
# Constants.
#
UNASGN = 'UNASSIGNED'


#
# Containers for management of timer creation/destruction.
#

class Stack(object):

    def __init__(self, obj_class):
        self.stack = []
        self.obj_class = obj_class

    def create_next(self, *args, **kwargs):
        self.stack.append(self.obj_class(*args, **kwargs))
        return self.stack_return()

    def remove_last(self):
        try:
            self.stack.pop()
        except IndexError:
            pass
        finally:
            return self.stack_return()

    def stack_return(self):
        current = None if len(self.stack) < 1 else self.stack[-1]
        previous = None if len(self.stack) < 2 else self.stack[-2]
        return current, previous

    def __len__(self):
        return len(self.stack)

    def __getitem__(self, key):
        return self.stack[key]


timer_stack = Stack(Timer)
loop_stack = Stack(Loop)


#
# Shortcut variables.
#
tf = None  # top of timer stack: 'Timer in Focus'
rf = None  # tf.times: 'Times (Record) in Focus'
sf = None  # tf.times.stamps: 'Stamps in Focus'
lf = None  # loop_stack.focus: 'Loop in Focus'
tfmin1 = None  # second from the top of timer stack 'tf minus 1' (for named loops)


#
# Shortcut functions.
#

def create_next_timer(*args, **kwargs):
    global tf, rf, sf, tfmin1
    tf, tfmin1 = timer_stack.create_next(*args, **kwargs)
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps
    return tf


def remove_last_timer():
    global tf, rf, sf, tfmin1
    tf, tfmin1 = timer_stack.remove_last()
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps


def create_next_loop(*args, **kwargs):
    global lf
    lf, _ = loop_stack.create_next(*args, **kwargs)


def remove_last_loop():
    global lf
    lf, _ = loop_stack.remove_last()


def refresh_shortcuts():
    global tf, rf, sf, tfmin1, lf
    tf, tfmin1 = timer_stack.stack_return()
    rf = None if tf is None else tf.times
    sf = None if rf is None else rf.stamps
    lf, _ = loop_stack.stack_return()


#
# Initialization.
#

root_timer = create_next_timer('root')  # (user may not remove)
