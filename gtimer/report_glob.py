
"""
Reporting functions acting on global variables (all are exposed to user).
"""

import data_glob as g
import report_loc
from timer_classes import Times

#
# Reporting functions to expose to the user.
#


def report(times=None, include_itrs=True, delim_mode=False):
    if times is None:
        return report_loc.report(g.root_timer.times, include_itrs, delim_mode)
    else:
        if not isinstance(Times):
            raise TypeError('Need a Times object to report (default is root).')
        return report_loc.report(times, include_itrs, delim_mode)


def write_structure(times=None):
    if times is None:
        return report_loc.write_structure(g.root_timer.times)
    else:
        if not isinstance(Times):
            raise TypeError('Need a Times object to write structure (default is root).')
        return report_loc.write_structure(times)
