
"""
Placing this here to avoid circular imports.
"""

import copy

from gtimer.private import glob as g


def copy_timer_stack():
    stack_copy = copy.deepcopy(g.timer_stack)
    # Recreate the dump relationships.
    for i in range(1, len(g.timer_stack)):
        name = stack_copy[i].name
        if g.timer_stack[i].dump is None:
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


def get_current_timer():
    return g.tf
