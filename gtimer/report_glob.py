
"""
Reporting functions acting on global variables (all are exposed to user).
"""

import data_glob as g
import report_loc
from timer_classes import Times
import mgmt_priv
from timeit import default_timer as timer

#
# Reporting functions to expose to the user.
#


def report(times=None,
           include_itrs=True,
           delim_mode=False,
           format_options=dict()):
    if times is None:
        if g.root_timer.stopped:
            return report_loc.report(g.root_timer.times,
                                     include_itrs,
                                     delim_mode,
                                     format_options)
        else:
            t = timer()
            rep = report_loc.report(mgmt_priv.collapse_times(),
                                    include_itrs,
                                    delim_mode,
                                    format_options)
            g.root_timer.self_cut += timer() - t
            return rep
    else:
        if not isinstance(times, Times):
            raise TypeError('Need a Times object to report (default is root).')
        return report_loc.report(times, include_itrs, delim_mode)


def compare(times_list=None,
            name=None,
            include_list=True,
            include_stats=True,
            delim_mode=False,
            format_options=dict()):
    if times_list is None:
        rep = ''
        for _, par_dict in g.root_timer.times.par_subdvsn.iteritems():
            for par_name, par_list in par_dict.iteritems():
                rep += report_loc.compare(par_list,
                                          par_name,
                                          include_list,
                                          include_stats,
                                          delim_mode,
                                          format_options)
    else:
        if not isinstance(times_list, (list, tuple)):
            raise TypeError("Expected a list or tuple of times for times_list.")
        if not all([isinstance(times, Times) for times in times_list]):
            raise TypeError("At least one member of times_list is not a Times object.")
        rep = report_loc.compare(times_list,
                                 name,
                                 include_list,
                                 include_stats,
                                 delim_mode,
                                 format_options)
    return rep


def write_structure(times=None):
    if times is None:
        return report_loc.write_structure(g.root_timer.times)
    else:
        if not isinstance(times, Times):
            raise TypeError('Need a Times object to write structure (default is root).')
        return report_loc.write_structure(times)
