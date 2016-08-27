# Main file that gets imported.

import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True

if DISABLED:
    from disabled.timer_glob_d import *
    from disabled.loop_d import *
    from disabled.timer_mgmt_d import *
    from disabled.report_glob_d import *
else:
    from timer_glob import *
    from loop import *
    from mgmt_pub import *
    from report_glob import *



#
#                  ...TO DO...
#
# 11. make my own error classes?
# 15. DUH: MULTIPROCESSING!!!
# 16. Reporting in the middle of timing...?
# 17. Test behavior in un-timed loop inside of timed loop
# 18. Make a reporting function that takes many timers (i.e. many
#     different runs of the same program), and makes tables of all
#     their stamps.  So that each table has TIMER on one axis and
#     STAMP on the other...yes this is what I'm really after!
# 10. stamp itr statistics (running avg, running stdev?)

# .
# .
# N+1. Automate the shortcut building.
#
#
#               ... LOW PRIORITY...
# 8. How to handle multiple separate heap (contexts)? Is this even useful?
# 14. NO_CHECK mode? 
#
#
#               .. to DONE...
# 19. Need to write a getter for the times then. A: used the old deep
#     copy had written previously.
# 22. provide function to hard reset current timer. >> could go wrong
#     if done inside a loop? A: yup, disallowed that.
# 20. stamp behavior in loop...if allowed duplicate, act like disjoint
#     stamp within loop, but still use loop mehanism to assign to same
#     iteration the following times a stamp is encountered. A: Yup this
#     is much better, and gets rid of l_stamp!!! finally!!
# 19. save_itrs as option
# 7. Once the Times class is stabilized, all the reporting
#     stuff that I wanted to do before.
# 13. DISABLE mode.
# 5. Self time and all that. (aggregation)
# 9. Stamps ordered AND register stamps
# 18. loop break / loop continue
# 6. Allow duplicate.
# 12. pause & resume
# 3. Auto-focus manager for subfunctions.
# 4. Test, test!
# 1. **Get the child-parent timer relationships working.**
# 2. Test, test
# 9. Get code files organized into global funcs and private funcs.
# N. Think about how much of focus manager to expose
#     to the user for manual manipulation. A: timer_mgmt
#