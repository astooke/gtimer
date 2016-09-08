
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
    """
    Produce a formatted report of the current timing data.

    Notes:
        When reporting a collection of parallel subdivisions, only the one with
        the greatest total time is reported on, and the rest are ignored (no
        branching).  To compare parallel subdivisions use compare().

    Args:
        times (Times, optional): Times object to report on.  If not provided,
            uses current root timer.
        include_itrs (bool, optional): Display invidual iteration times.
        include_stats (bool, optional): Display iteration statistics.
        delim_mode (bool, optional): If True, format for spreadsheet.
        format_options (dict, optional): Formatting options, see below.

    Formatting Keywords & Defaults:
        Human-Readable Mode
            - 'stamp_name_width': 20
            - 'itr_tab_width': 2
            - 'itr_num_width': 6
            - 'itr_name_width': 12
            - 'indent_symbol': '  ' (two spaces)
            - 'parallel_symbol': '(par)'
        Delimited Mode
            - 'delimiter': '\t' (tab)
            - 'ident_symbol': '+'
            - 'parallel_symbol': '(par)'

    Returns:
        str: Timing data report as formatted string.

    Raises:
        TypeError: If 'times' param is used and value is not a Times object.
    """
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
                                    format_options,
                                    timer_state='running')
            f.root.self_cut += timer() - t
            return rep
    else:
        if not isinstance(times, Times):
            raise TypeError("Expected Times instance for param 'times' (default is root).")
        return report_loc.report(times,
                                 include_itrs,
                                 include_stats,
                                 delim_mode,
                                 format_options)


def compare(times_list=None,
            name=None,
            include_list=True,
            include_stats=True,
            delim_mode=False,
            format_options=None):
    """
    Produce a formatted comparison of timing datas.

    Notes:
        If no times_list is provided, produces comparison reports on all parallel
        subdivisions present at the root level of the current timer.  To compare
        parallel subdivisions at a lower level, get the times data, navigate
        within it to the parallel list of interest, and provide that as input
        here.  As with report(), any further parallel subdivisions encountered
        have only their member with the greatest total time reported on (no
        branching).

    Args:
        times_list (Times, optional): list or tuple of Times objects.  If not
            provided, uses current root timer.
        name (any, optional): Identifier, passed through str().
        include_list (bool, optional): Display stamps hierarchy.
        include_stats (bool, optional): Display stamp comparison statistics.
        delim_mode (bool, optional): If True, format for spreadsheet.
        format_options (None, optional): Formatting options, see below.

    Formatting Keywords & Defaults:
        Human-readable Mode
            - 'stamp_name_width': 18
            - 'list_column_width': 12
            - 'list_tab_width': 2
            - 'stat_column_width': 8
            - 'stat_tab_width': 2
            - 'indent_symbol: ' ' (one space)
        Delimited Mode
            - 'delimiter': '\t' (tab)
            - 'ident_symbol': '+'

    Returns:
        str: Times data comparison as formatted string.

    Raises:
        TypeError: If any element of provided collection is not a Times object.
    """
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
    """
    Produce a formatted record of a times data structure.

    Args:
        times (Times, optional): If not provided, uses the current root timer.

    Returns:
        str: Timer tree hierarchy in a formatted string.

    Raises:
        TypeError: If provided argument is not a Times object.
    """
    if times is None:
        return report_loc.write_structure(f.root.times)
    else:
        if not isinstance(times, Times):
            raise TypeError("Expected Times instance for param 'times' (default is root).")
        return report_loc.write_structure(times)
