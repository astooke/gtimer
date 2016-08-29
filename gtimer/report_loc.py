
"""
Reporting functions acting on locally provided variables (hidden from user).
"""

from data_glob import UNASGN


#
# Functions to expose elsewhere in package.
#


def report(times, include_itrs=True, delim_mode=False, format_options=dict()):
    FMTS = _define_formats(delim_mode, format_options)
    rep = FMTS['BEGIN'].format(times.name)
    rep += _header(times, FMTS['Header'])
    rep += FMTS['INT']
    rep += _report_stamps(times, FMTS['Stamps'])
    if include_itrs:
        rep_itrs = _report_itrs(times, FMTS['Itrs'], delim_mode)
        if rep_itrs:
            rep += FMTS['ITR']
            rep += rep_itrs
    rep += FMTS['END'].format(times.name)
    return rep


def write_structure(times):
    strct = '\n---Times Data Tree---\n'
    strct += _write_structure(times)
    strct += "\n\n"
    return strct


#
# Private helper functions.
#


def _define_formats(delim_mode, fmt_opts):
    delim_mode = bool(delim_mode)
    if not isinstance(fmt_opts, dict):
        raise TypeError("Expected dictionary for format_options input.")
    if delim_mode:
        DELIM = '\t' if 'delimiter' not in fmt_opts else str(fmt_opts['delimiter'])
        BEGIN = "Timer Report ({})\n"  # accepts: times.name
        INT = "Intervals\n"
        ITR = "\n\nLoop Iterations\n"
        END = "End ({})"  # accepts: times.name
        HDR = {
            'HDR_STR': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
            'HDR_FLT': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
            'APND': ''
        }
        STMP = {
            'STMP': "\n{{}}{{}}{}{{}}".format(DELIM),  # accepts: indent, label, value
            'IDT_SYM': '+',
            'SPC': '',
        }
        ITRS = {
            'HDR': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
            'APND': '',
            'STMP': "{}{{}}".format(DELIM),  # accepts: label
            'ITR': "\n{}",  # accepts: value
            'VAL': "{}{{}}".format(DELIM),  # accepts: value
            'NON': "{}".format(DELIM),
        }
    else:
        STMP_NAME = 20 if 'stamp_name_width' not in fmt_opts else int(fmt_opts['stamp_name_width'])
        ITR_TAB = 2 if 'itr_tab_width' not in fmt_opts else int(fmt_opts['itr_tab_width'])
        ITR_NUM = 6 if 'itr_num_width' not in fmt_opts else int(fmt_opts['itr_num_width'])
        ITR_NAME = 14 if 'itr_name_width' not in fmt_opts else int(fmt_opts['itr_name_width'])
        if ITR_TAB < 1 or ITR_NUM < 1 or ITR_NAME < 1:
            raise ValueError("Cannot have any width less than 1.")
        ITR_SPC = ITR_TAB + ITR_NAME - ITR_NUM
        if ITR_SPC < 0:
            raise ValueError("Cannot have widths: tab + itr_name - itr_num < 0.")
        BEGIN = "\n---Begin Timer Report ({})---"  # accepts: times.name
        INT = "\n\n\nIntervals\n---------"
        ITR = "\n\n\nLoop Iterations\n---------------"
        END = "\n---End Timer Report ({})---\n"  # accepts, times.name
        HDR = {
            'HDR_STR': "\n{:<20} {}",  # accepts: label, value
            'HDR_FLT': "\n{:<20} {:.4g}",  # accepts: label, value
            'APND': ':'
        }
        STMP = {
            'STMP': "\n{{}}{{:.<{}}} {{:.4g}}".format(STMP_NAME),  # acepts: indent, label, value
            'IDT_SYM': '  ',
            'SPC': ' ',
        }
        ITRS = {
            'HDR': "\n{:<12} {}",  # accepts: label, value
            'APND': ':',
            'STMP': "{0}{{:>{1}.{1}}}".format(' ' * ITR_TAB, ITR_NAME),  # accepts: label
            'ITR': "\n{:<5,}",  # accepts: value
            'VAL': "{}{{:{}.2f}}".format(' ' * ITR_SPC, ITR_NUM),  # accepts: value
            'NON': "{}".format(' ' * (ITR_TAB + ITR_NAME)),
            'ITR_TAB': ITR_TAB,
            'ITR_NAME': ITR_NAME
        }
    FMTS = {'Header': HDR, 'Stamps': STMP, 'Itrs': ITRS,
            'BEGIN': BEGIN, 'INT': INT, 'ITR': ITR, 'END': END}
    return FMTS


def _header(times, FMTS):
    rep = FMTS['HDR_STR'].format('Timer Name' + FMTS['APND'], times.name)
    rep += FMTS['HDR_FLT'].format('Total Time (s)' + FMTS['APND'], times.total)
    rep += FMTS['HDR_FLT'].format('Self Time (Agg.)' + FMTS['APND'], times.self_agg)
    return rep


def _report_stamps(times, FMTS, indent=0):
    stamps = times.stamps
    rep_stmps = ''
    for stamp in stamps.order:
        rep_stmps += FMTS['STMP'].format(FMTS['IDT_SYM'] * indent, stamp + FMTS['SPC'], stamps.cum[stamp])
        if stamp in times.subdivisions:
            for sub_times in times.subdivisions[stamp]:
                rep_stmps += _report_stamps(sub_times, FMTS, indent + 1)
    if UNASGN in times.subdivisions:
        rep_stmps += "\n{}{}".format(FMTS['IDT_SYM'] * indent, UNASGN)
        for sub_times in times.subdivisions[UNASGN]:
            rep_stmps += _report_stamps(sub_times, FMTS, indent + 1)
    return rep_stmps


def _report_itrs(times, FMTS, delim_mode=False):
    rep = ''
    stamps = times.stamps
    if stamps.itrs:
        rep += "\n"
        rep += FMTS['HDR'].format('Timer' + FMTS['APND'], times.name)
        if times.parent is not None:
            lin_str = _fmt_lineage(_get_lineage(times))
            rep += FMTS['HDR'].format('Lineage' + FMTS['APND'], lin_str)
        rep += "\n\nIter."
        itrs_order = []
        is_key_active = []
        for stamp in stamps.order:
            if stamp in stamps.itrs:
                itrs_order += [stamp]
                is_key_active += [True]  # (List needed for any() usage.)
        for stamp in itrs_order:
            rep += FMTS['STMP'].format(stamp)
        if not delim_mode:
            rep += "\n-----"
            for stamp in itrs_order:
                rep += "{}{{:>{}}}".format(' ' * FMTS['ITR_TAB'], FMTS['ITR_NAME']).format('-------')
        itr = 0
        while any(is_key_active):  # (Must be a list)
            next_line = FMTS['ITR'].format(itr)
            for i, stamp in enumerate(itrs_order):
                if is_key_active[i]:
                    try:
                        val = stamps.itrs[stamp][itr]
                        next_line += FMTS['VAL'].format(val)
                    except IndexError:
                        next_line += FMTS['NON']
                        is_key_active[i] = False
                else:
                    next_line += FMTS['NON']
            if any(is_key_active):
                rep += next_line
            itr += 1
        rep += "\n"
    for _, subdivisions in times.subdivisions.iteritems():
        for sub_times in subdivisions:
            rep += _report_itrs(sub_times, FMTS, delim_mode)
    return rep


def _get_lineage(times):
    if times.parent is not None:
        return _get_lineage(times.parent) + ((times.parent.name, times.pos_in_parent), )
    else:
        return tuple()


def _fmt_lineage(lineage):
    lin_str = ''
    for link in lineage:
        lin_str += "{} ({})--> ".format(link[0], link[1])
    try:
        return lin_str[:-4]
    except IndexError:
        pass


def _write_structure(times, indent=0):
    strct = "\n{}{}".format(' ' * indent, times.name)
    if times.pos_in_parent:
        strct += " ({})".format(times.pos_in_parent)
    for _, sub_list in times.subdivisions.iteritems():
        for sub_times in sub_list:
            strct += _write_structure(sub_times, indent=indent + 4)
    for _, par_sub_dict in times.par_subdivisions.iteritems():
        for _, par_sub_list in par_sub_dict.iteritems():
            strct += _write_structure(par_sub_list[0], indent=indent + 4)
    return strct
