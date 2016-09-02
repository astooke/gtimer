#
# Capturing the current times data during timing.
#

import copy

from gtimer.private import glob as g
from gtimer.private import mgmt
from gtimer.public import timer as timer_glob
from gtimer.private.util import copy_timer_stack


def collapse_subdivision():
    if g.tf.in_loop:
        mgmt.loop_end(end_stamp_unique=False)
        mgmt.exit_loop()
    else:
        timer_glob.stop()
        g.remove_last_timer()


def collapse_times():
    """Make copies of everything, assign to global shortcuts so functions work
    on them, extract the times, then restore the running stacks.
    """
    orig_ts = g.timer_stack
    orig_ls = g.loop_stack
    copy_ts = copy_timer_stack()
    copy_ls = copy.deepcopy(g.loop_stack)
    g.timer_stack = copy_ts
    g.loop_stack = copy_ls
    g.refresh_shortcuts()
    while len(g.timer_stack) > 1:
        collapse_subdivision()
    timer_glob.stop()
    collapsed_times = g.rf
    g.timer_stack = orig_ts  # (loops throw error if not same object!)
    g.loop_stack = orig_ls
    g.refresh_shortcuts()
    return collapsed_times
