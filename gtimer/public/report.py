
"""
Reporting functions provided to user.
"""

from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.local import report as report_loc
from gtimer.local.times import Times
from gtimer.private import collapse

__all__ = ['report', 'compare', 'write_structure']


#
# Reporting functions to expose to the user.
#


def report(times=None,
           include_itrs=True,
           include_stats=True,
           delim_mode=False,
           format_options=None):
    if times is None:
        if f.root.stopped:
            return report_loc.report(f.root.times,
                                     include_itrs,
                                     include_stats,
                                     delim_mode,
                                     format_options)
        else:
            t = timer()
            rep = report_loc.report(collapse.collapse_times(),
                                    include_itrs,
                                    include_stats,
                                    delim_mode,
                                    format_options)
            f.root.self_cut += timer() - t
            return rep
    else:
        if not isinstance(times, Times):
            raise TypeError("Expected Times instance for param 'times' (default is root).")
        return report_loc.report(times, include_itrs, delim_mode)


def compare(times_list=None,
            name=None,
            include_list=True,
            include_stats=True,
            delim_mode=False,
            format_options=None):
    if times_list is None:
        rep = ''
        for _, par_dict in f.root.times.par_subdvsn.iteritems():
            for par_name, par_list in par_dict.iteritems():
                rep += report_loc.compare(par_list,
                                          par_name,
                                          include_list,
                                          include_stats,
                                          delim_mode,
                                          format_options)
    else:
        if not isinstance(times_list, (list, tuple)):
            raise TypeError("Expected a list/tuple of times instances for param 'times_list'.")
        if not all([isinstance(times, Times) for times in times_list]):
            raise TypeError("At least one member of param 'times_list' is not a Times object.")
        rep = report_loc.compare(times_list,
                                 name,
                                 include_list,
                                 include_stats,
                                 delim_mode,
                                 format_options)
    return rep


def write_structure(times=None):
    if times is None:
        return report_loc.write_structure(f.root.times)
    else:
        if not isinstance(times, Times):
            raise TypeError("Expected Times instance for param 'times' (default is root).")
        return report_loc.write_structure(times)
