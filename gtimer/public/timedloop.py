
"""
Factory functions providing timed loop objects to user.
"""


from gtimer.private.timedloop import TimedLoop, TimedFor
from gtimer.public.timer import SET

__all__ = ['timed_loop', 'timed_for']


def timed_loop(name=None,
               rgstr_stamps=None,
               save_itrs=SET['SI'],
               loop_end_stamp=None,
               end_stamp_unique=SET['UN'],
               keep_prev_subdivisions=SET['KS'],
               keep_end_subdivisions=SET['KS'],
               quick_print=SET['QP']):
    """
    Instantiate a TimedLoop object for measuring loop iteration timing data.
    Can be used with either for or while loops.

    Example::

        loop = timed_loop()
        while x > 0:  # or for x in <iterable>:
            next(loop)  # or loop.next()
            <body of loop, with gtimer stamps>
        loop.exit()

    Notes:
        Can be used as a context manager around the loop, without requiring
        separate call to exit().  Redundant calls to exit() do no harm.  Loop
        functionality is implemented in the next() or __next__() methods.

        Each instance can only be used once, so for an inner loop, this function
        must be called within the outer loop.

        Any awaiting subdivisions kept at entrance to a loop section will go to
        the 'UNASSIGNED' position to indicate that they are not properly accounted
        for in the hierarchy.  Likewise for any awaiting subdivisions kept at the
        end of loop iterations without a named stamp.

    Args:
        name (any, optional): Identifier (makes the loop a subdivision), passed
            through str().
        rgstr_stamps (list, tuple, optional): Identifiers, see subdivision().
        save_itrs (bool, optional): see subdivision().
        loop_end_stamp (any, optional): Identifier, automatic stamp at end of
            every iteration.
        end_stamp_unique (bool, optional): see stamp().
        keep_prev_subdivisions (bool, optional): Keep awaiting subdivisions on
            entering loop.
        keep_end_subdivisions (bool, optional): Keep awaiting subdivisions at
            end of iterations.
        quick_print (bool, optional): Named loop only, print at end of each iteration.

    Returns:
        TimedLoop: Custom gtimer object for measuring loops.
    """
    return TimedLoop(name=name,
                     rgstr_stamps=rgstr_stamps,
                     save_itrs=save_itrs,
                     loop_end_stamp=loop_end_stamp,
                     end_stamp_unique=end_stamp_unique,
                     keep_prev_subdivisions=keep_prev_subdivisions,
                     keep_end_subdivisions=keep_end_subdivisions)


def timed_for(iterable,
              name=None,
              rgstr_stamps=None,
              save_itrs=SET['SI'],
              loop_end_stamp=None,
              end_stamp_unique=SET['UN'],
              keep_prev_subdivisions=SET['KS'],
              keep_end_subdivisions=SET['KS'],
              quick_print=SET['QP']):
    """
    Instantiate a TimedLoop object for measuring for loop iteration timing data.
    Can be used only on for loops.

    Example::

        for i in gtimer.timed_for(iterable, ..):
            <body of loop with gtimer stamps>

    Notes:
        Can be used as a context manager around the loop.  When breaking out of
        the loop, requires usage either as a context manager or with a reference
        to the object on which to call the exit() method after leaving the loop
        body.  Redundant calls to exit() do no harm.  Loop functionality is
        implemented in the __iter__() method.

        Each instance can only be used once, so for an inner loop, this function
        must be called within the outer loop.

        Any awaiting subdivisions kept at entrance to a loop section will go to
        the 'UNASSIGNED' position to indicate that they are not properly accounted
        for in the hierarchy.  Likewise for any awaiting subdivisions kept at the
        end of loop iterations without a named stamp.

    Args:
        iterable: Same as provided to regular 'for' command.
        name (any, optional): Identifier (makes the loop a subdivision), passed
            through str().
        rgstr_stamps (list,tuple, optional): Identifiers, see subdivision().
        save_itrs (bool, optional): see subdivision().
        loop_end_stamp (any, optional): Identifier, automatic stamp at end of
            every iteration, passed through str().
        end_stamp_unique (bool, optional): see stamp().
        keep_prev_subdivisions (bool, optional): Keep awaiting subdivisions on
            entering loop.
        keep_end_subdivisions (bool, optional): Keep awaiting subdivisions at
            end of iterations.
        quick_print (bool, optional): Named loop only, print at end of each iteration.


    Returns:
        TimedFor: Custom gtimer object for measuring for loops.
    """
    return TimedFor(iterable,
                    name=name,
                    rgstr_stamps=rgstr_stamps,
                    save_itrs=save_itrs,
                    loop_end_stamp=loop_end_stamp,
                    end_stamp_unique=end_stamp_unique,
                    keep_prev_subdivisions=keep_prev_subdivisions,
                    keep_end_subdivisions=keep_end_subdivisions)
