
"""
Reporting functions acting on locally provided variables (hidden from user).
"""

from data_glob import UNASGN


#
# Report formatting values (text mode and delimited mode).
#

TAB_WIDTH = 2
ITR_WIDTH = 6
NAME_WIDTH = 14
ITR_SPC = TAB_WIDTH + NAME_WIDTH - ITR_WIDTH
DELIM = '\t'

HDR_DEL = {
    'HDR_STR': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
    'HDR_FLT': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
    'APND': ''
}
HDR_TXT = {
    'HDR_STR': "\n{:<20} {}",  # accepts: label, value
    'HDR_FLT': "\n{:<20} {:.4g}",  # accepts: label, value
    'APND': ':'
}

STMP_DEL = {
    'STMP': "\n{{}}{{}}{}{{}}".format(DELIM),  # accepts: indent, label, value
    'IDT_SYM': '+',
    'SPC': '',
}
STMP_TXT = {
    'STMP': "\n{}{:.<14} {:.4g}",  # acepts: indent, label, value
    'IDT_SYM': '  ',
    'SPC': ' ',
}

ITRS_DEL = {
    'HDR': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
    'APND': '',
    'STMP': "{}{{}}".format(DELIM),  # accepts: label
    'ITR': "\n{}",  # accepts: value
    'VAL': "{}{{}}".format(DELIM),  # accepts: value
    'NON': "{}".format(DELIM),
}
ITRS_TXT = {
    'HDR': "\n{:<12} {}",  # accepts: label, value
    'APND': ':',
    'STMP': "{0}{{:>{1}.{1}}}".format(' ' * TAB_WIDTH, NAME_WIDTH),  # accepts: label
    'ITR': "\n{:<5,}",  # accepts: value
    'VAL': "{}{{:{}.2f}}".format(' ' * ITR_SPC, ITR_WIDTH),  # accepts: value
    'NON': "{}".format(' ' * (TAB_WIDTH + NAME_WIDTH)),
}

FMTS_DEL = {
    'Header': HDR_DEL,
    'Stamps': STMP_DEL,
    'Itrs': ITRS_DEL,
}
FMTS_TXT = {
    'Header': HDR_TXT,
    'Stamps': STMP_TXT,
    'Itrs': ITRS_TXT,
}

#
# Functions to expose elsewhere in package.
#


def report(times, include_itrs=True, delim_mode=False):
    if delim_mode:
        FMTS = FMTS_DEL
        rep = "Timer Report\n"
        INT = "\n\nIntervals\n"
        ITR = "\n\nLoop Iterations\n"
        END = ""
    else:
        FMTS = FMTS_TXT
        rep = "\n---Begin Timer Report ({})---".format(times.name)
        INT = "\n\n\nIntervals\n---------"
        ITR = "\n\n\nLoop Iterations\n---------------"
        END = "\n---End Timer Report ({})---\n".format(times.name)
    rep += _header(times, FMTS['Header'])
    rep += INT
    rep += _report_stamps(times, FMTS['Stamps'])
    if include_itrs:
        rep_itrs = _report_itrs(times, FMTS['Itrs'], delim_mode)
        if rep_itrs:
            rep += ITR
            rep += rep_itrs
    rep += END
    return rep


def write_structure(times):
    strct = '\n---Times Data Tree---\n'
    strct += _write_structure(times)
    strct += "\n\n"
    return strct


#
# Private helper functions.
#


def _header(times, FMTS):
    rep = FMTS['HDR_STR'].format('Timer Name' + FMTS['APND'], times.name)
    rep += FMTS['HDR_FLT'].format('Total Time (s)' + FMTS['APND'], times.total)
    rep += FMTS['HDR_FLT'].format('Self Time Agg' + FMTS['APND'], times.self_agg)
    rep += FMTS['HDR_FLT'].format('Self Time Cut' + FMTS['APND'], times.self_cut)
    return rep


def _report_stamps(times, FMTS, indent=0):
    stamps = times.stamps
    rep_stmps = ''
    for stamp in stamps.order:
        rep_stmps += FMTS['STMP'].format(FMTS['IDT_SYM'] * indent, stamp + FMTS['SPC'], stamps.cum[stamp])
        if stamp in times.children:
            for child in times.children[stamp]:
                rep_stmps += _report_stamps(child, FMTS, indent + 1)
    if UNASGN in times.children:
        rep_stmps += "\n{}{}".format(FMTS['IDT_SYM'] * indent, UNASGN)
        for child in times.children[UNASGN]:
            rep_stmps += _report_stamps(child, FMTS, indent + 1)
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
                rep += "{}{{:>{}}}".format(' ' * TAB_WIDTH, NAME_WIDTH).format('-------')
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
    for _, children in times.children.iteritems():
        for child in children:
            rep += _report_itrs(child, FMTS, delim_mode)
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
    for _, child_list in times.children.iteritems():
        for child in child_list:
            strct += _write_structure(child, indent=indent + 4)
    return strct