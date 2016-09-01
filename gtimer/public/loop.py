

from gtimer.private.loop import TimedLoop, TimedFor

__all__ = ['timed_loop', 'timed_for']


def timed_loop(name=None,
               rgstr_stamps=list(),
               save_itrs=True,
               loop_end_stamp=None,
               end_stamp_unique=True,
               keep_prev_subdivisions=True,
               keep_end_subdivisions=True):
    return TimedLoop(name=name,
                     rgstr_stamps=rgstr_stamps,
                     save_itrs=save_itrs,
                     loop_end_stamp=loop_end_stamp,
                     end_stamp_unique=end_stamp_unique,
                     keep_prev_subdivisions=keep_prev_subdivisions,
                     keep_end_subdivisions=keep_end_subdivisions)


def timed_for(iterable,
              name=None,
              rgstr_stamps=list(),
              save_itrs=True,
              loop_end_stamp=None,
              end_stamp_unique=True,
              keep_prev_subdivisions=True,
              keep_end_subdivisions=True):
    return TimedFor(iterable,
                    name=name,
                    rgstr_stamps=rgstr_stamps,
                    save_itrs=save_itrs,
                    loop_end_stamp=loop_end_stamp,
                    end_stamp_unique=end_stamp_unique,
                    keep_prev_subdivisions=keep_prev_subdivisions,
                    keep_end_subdivisions=keep_end_subdivisions)
