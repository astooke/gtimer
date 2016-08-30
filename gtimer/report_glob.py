
"""
Reporting functions acting on global variables (all are exposed to user).
"""

import data_glob as g
import report_loc
from timer_classes import Times

#
# Reporting functions to expose to the user.
#


def report(times=None,
           include_itrs=True,
           delim_mode=False,
           format_options=dict()):
    if times is None:
        return report_loc.report(g.root_timer.times, include_itrs, delim_mode)
    else:
        if not isinstance(times, Times):
            raise TypeError('Need a Times object to report (default is root).')
        return report_loc.report(times, include_itrs, delim_mode)


def compare(times_list=None,
            include_list=True,
            include_stats=True,
            delim_mode=False,
            format_options=dict()):
    if times_list is None:
        rep = ''
        for _, par_dict in g.root_timer.times.par_subdivisions:
            for _, par_list in par_dict.iteritems():
                rep += report_loc.compare(par_list,
                                          include_list,
                                          include_stats,
                                          delim_mode,
                                          format_options)
    else:
        if not isinstance(times_list, (list, tuple)):
            raise TypeError("Expected a list or tuple of times for times_list.")
        for times in times_list:
            if not isinstance(times, Times):
                raise TypeError("At least one member of times_list is not a Times object.")
        rep = report_loc.compare(times_list,
                                 include_list,
                                 include_stats,
                                 delim_mode,
                                 format_options)
    return rep


def write_structure(times=None):
    if times is None:
        return report_loc.write_structure(g.root_timer.times)
    else:
        if not isinstance(Times):
            raise TypeError('Need a Times object to write structure (default is root).')
        return report_loc.write_structure(times)
