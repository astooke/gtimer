
"""
When the timer is still active and the user requests times data or reports,
this internal functionality retrieves the current data from the active timer
data structure.
"""

import copy

from gtimer.private import focus as f
from gtimer.private import loop
from gtimer.public import timer as timer_pub


def collapse_times():
    """Make copies of everything, assign to global shortcuts so functions work
    on them, extract the times, then restore the running stacks.
    """
    orig_ts = f.timer_stack
    orig_ls = f.loop_stack
    copy_ts = _copy_timer_stack()
    copy_ls = copy.deepcopy(f.loop_stack)
    f.timer_stack = copy_ts
    f.loop_stack = copy_ls
    f.refresh_shortcuts()
    while (len(f.timer_stack) > 1) or f.t.in_loop:
        _collapse_subdivision()
    timer_pub.stop()
    collapsed_times = f.r
    f.timer_stack = orig_ts  # (loops throw error if not same object!)
    f.loop_stack = orig_ls
    f.refresh_shortcuts()
    return collapsed_times


def _collapse_subdivision():
    if f.t.in_loop:
        loop.loop_end(end_stamp_unique=False)
        loop.exit_loop()
    else:
        timer_pub.stop()
        f.remove_last_timer()


def _copy_timer_stack():
    stack_copy = copy.deepcopy(f.timer_stack)
    # Recreate the dump relationships.
    for i in range(1, len(f.timer_stack)):
        name = stack_copy[i].name
        if f.timer_stack[i].dump is None:
            if stack_copy[i].named_loop:
                stack_copy[i - 1].times.subdvsn[name] = [stack_copy[i].times]
            else:
                stack_copy[i - 1].subdvsn_awaiting[name] = stack_copy[i].times
        else:
            if stack_copy[i].named_loop:
                stack_copy[i].dump = stack_copy[i - 1].times.subdvsn[name]
            else:
                stack_copy[i].dump = stack_copy[i - 1].subdvsn_awaiting[name]
    return stack_copy
