# Main file that gets imported.

import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True

if DISABLED:
    # Contents of these might be out of date.
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
# 18. Make a reporting function that takes many timers (i.e. many
#     different runs of the same program), and makes tables of all
#     their stamps.  So that each table has TIMER on one axis and
#     STAMP on the other...yes this is what I'm really after!
# 10. stamp itr statistics (running avg, running stdev?)
# 23. re-think where we hold save_itrs just for its interaction with 
#     stamps_as_itrs
# 24. Fix tree traversal code to cope with parallel children?
# 25. print stamps from parallel like this: take the stamps from the one
#     that took the longest time.
# 26. print a parallel section like this: make the full tree of all the
#     stamps from all the parallel children, then leave a blank or a '--'
#     for the children who don't have that stamp.


#
#
#               ... LOW PRIORITY...
# 8. How to handle multiple separate heap (contexts)? Is this even useful?
# 14. NO_CHECK mode? X I don't think it's necessary.
#

#
#               .. to DONE...

# 17. Test behavior in un-timed loop inside of timed loop
# 27. Protect against user closing a timer...should also protect against
#     automated closing of user timer!
# 25. Possible redundant aggregate_up_self in assign children, because
#     I do them all at the beginning there, but also in the first call
#     to merge_times.  Probably better to remove from merge_times and just
#     execute as a separate call. A: Yup fixed this (quite different now)!
# N+1. Automate the shortcut building.
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