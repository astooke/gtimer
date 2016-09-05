
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
    return TimedFor(iterable,
                    name=name,
                    rgstr_stamps=rgstr_stamps,
                    save_itrs=save_itrs,
                    loop_end_stamp=loop_end_stamp,
                    end_stamp_unique=end_stamp_unique,
                    keep_prev_subdivisions=keep_prev_subdivisions,
                    keep_end_subdivisions=keep_end_subdivisions)
