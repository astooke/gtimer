
"""
Reporting functions acting on locally provided variables (hidden from user).
"""

from data_glob import UNASGN

#
# Functions to expose elsewhere in package.
#


def report(times, include_itrs=True, delim_mode=False, format_options=dict()):
    delim_mode = bool(delim_mode)
    _define_report_formats(delim_mode, format_options)
    FMT = FMTS_RPT['Report']
    rep = FMT['BEGIN'].format(times.name)
    rep += _report_header(times)
    rep += FMT['INT']
    rep += _report_stamps(times)
    if include_itrs:
        rep_itrs = _report_itrs(times, delim_mode)
        if rep_itrs:
            rep += FMT['ITR']
            rep += rep_itrs
    rep += FMT['END'].format(times.name)
    return rep


def compare(times_list,
            include_list=True,
            include_stats=True,
            delim_mode=False,
            format_options=dict()):

    delim_mode = bool(delim_mode)

    # Assemble data.
    master_stamps = CompareTimes()
    _build_master(master_stamps, times_list)

    # Write report.
    _define_compare_formats(delim_mode, format_options)
    rep = ''
    rep += "\n\n---Parallel / Comparison Report---"
    if include_list:
        rep += _compare_list(times_list, master_stamps, delim_mode)
    if include_stats:
        _populate_compare_stats(master_stamps)
        rep += _compare_stats(times_list, master_stamps, delim_mode)
    if not include_list and not include_stats:
        rep += "\n(Neither list nor stats selected for reporting.)\n"
    rep += "\n---End Parallel / Comparison Report---"
    return rep


def write_structure(times):
    strct = '\n---Times Data Tree---\n'
    strct += _write_structure(times)
    strct += "\n\n"
    return strct


#
# Private helper functions.
#


FMTS_RPT = None
FMTS_CMP = None


#
#  Reporting.
#

def _define_report_formats(delim_mode, fmt_opts):
    global FMTS_RPT
    if not isinstance(fmt_opts, dict):
        raise TypeError("Expected dictionary for format_options input.")
    if delim_mode:
        DELIM = '\t' if 'delimiter' not in fmt_opts else str(fmt_opts['delimiter'])

        RPRT = {
            'BEGIN': "Timer Report ({})\n",  # accepts: times.name
            'INT': "Intervals\n",
            'ITR': "\n\nLoop Iterations\n",
            'END': "End ({})"  # accepts: times.name
        }
        HDR = {
            'HDR_STR': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
            'HDR_FLT': "\n{{}}{}{{}}".format(DELIM),  # accepts: label, value
            'APND': ''
        }
        STMP = {
            'STMP': "\n{{}}{{}}{}{{}}".format(DELIM),  # accepts: indent, label, value
            'IDT_SYM': '+' if 'indent_symbol' not in fmt_opts else str(fmt_opts['indent_symbol']),
            'SPC': '',
            'PAR': '(par)' if 'parallel_symbol' not in fmt_opts else str(fmt_opts['parallel_symbol'])
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

        RPRT = {
            'BEGIN': "\n---Begin Timer Report ({})---",  # accepts: times.name
            'INT': "\n\n\nIntervals\n---------",
            'ITR': "\n\n\nLoop Iterations\n---------------",
            'END': "\n---End Timer Report ({})---\n",  # accepts, times.name
        }
        HDR = {
            'HDR_STR': "\n{:<20} {}",  # accepts: label, value
            'HDR_FLT': "\n{:<20} {:.4g}",  # accepts: label, value
            'APND': ':'
        }
        STMP = {
            'STMP': "\n{{}}{{:.<{}}} {{:.4g}}".format(STMP_NAME),  # acepts: indent, label, value
            'IDT_SYM': '  ' if 'indent_symbol' not in fmt_opts else str(fmt_opts['indent_symbol']),
            'SPC': ' ',
            'PAR': '(par)' if 'parallel_symbol' not in fmt_opts else str(fmt_opts['parallel_symbol'])

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
    FMTS_RPT = {'Report': RPRT, 'Header': HDR, 'Stamps': STMP, 'Itrs': ITRS}


def _report_header(times):
    FMT = FMTS_RPT['Header']
    rep = FMT['HDR_STR'].format('Timer Name' + FMT['APND'], times.name)
    rep += FMT['HDR_FLT'].format('Total Time (s)' + FMT['APND'], times.total)
    rep += FMT['HDR_FLT'].format('Self Time (Agg.)' + FMT['APND'], times.self_agg)
    return rep


def _report_stamps(times, indent=0, par=False):
    FMT = FMTS_RPT['Stamps']
    stamps = times.stamps
    rep = ''
    for stamp in stamps.order:
        stamp_str = stamp + FMT['SPC']
        stamp_str += FMT['PAR'] if par else ''
        rep += FMT['STMP'].format(FMT['IDT_SYM'] * indent, stamp_str, stamps.cum[stamp])
        if stamp in times.subdivisions:
            _report_sub_times(times.subidivions[stamp], indent, par=par)
        if stamp in times.par_subdivisions:
            _report_par_sub_times(times.par_subdivisions[stamp], indent)
    if UNASGN in times.subdivisions:
        rep += "\n{}{}".format(FMT['IDT_SYM'] * indent, UNASGN)
        _report_sub_times(times.subidivions[UNASGN], indent, par=par)
    if UNASGN in times.par_subdivisions:
        rep += "\n{}{}".format(FMT['IDT_SYM'] * indent, UNASGN)
        _report_par_sub_times(times.par_subdivisions[UNASGN], indent)
    return rep


def _report_sub_times(subdivisions, indent, par):
    rep = ''
    for sub_times in subdivisions:
        rep += _report_stamps(sub_times, indent + 1, par)
    return rep


def _report_par_sub_times(par_subdivisions, indent):
    FMT = FMTS_RPT['Stamp']
    rep = ''
    for par_name, par_list in par_subdivisions.iteritems():
        sub_with_max_tot = max(par_list, key=lambda x: x.total)
        rep += "\n{}{}".format(FMT['IDT_SYM'] * indent, par_name + FMT['PAR'])
        rep += _report_stamps(sub_with_max_tot, indent + 1, par=True)
    return rep


def _report_itrs(times, FMTS_RPT, delim_mode=False):
    FMT = FMTS_RPT['Itrs']
    rep = ''
    stamps = times.stamps
    if stamps.itrs:
        rep += "\n"
        rep += FMT['HDR'].format('Timer' + FMT['APND'], times.name)
        if times.parent is not None:
            lin_str = _fmt_lineage(_get_lineage(times))
            rep += FMT['HDR'].format('Lineage' + FMT['APND'], lin_str)
        rep += "\n\nIter."
        itrs_order = []
        is_key_active = []
        for stamp in stamps.order:
            if stamp in stamps.itrs:
                itrs_order += [stamp]
                is_key_active += [True]  # (List needed for any() usage.)
        for stamp in itrs_order:
            rep += FMT['STMP'].format(stamp)
        if not delim_mode:
            rep += "\n-----"
            for stamp in itrs_order:
                rep += "{}{{:>{}}}".format(' ' * FMT['ITR_TAB'], FMT['ITR_NAME']).format('-------')
        itr = 0
        while any(is_key_active):  # (Must be a list)
            next_line = FMT['ITR'].format(itr)
            for i, stamp in enumerate(itrs_order):
                if is_key_active[i]:
                    try:
                        val = stamps.itrs[stamp][itr]
                        next_line += FMT['VAL'].format(val)
                    except IndexError:
                        next_line += FMT['NON']
                        is_key_active[i] = False
                else:
                    next_line += FMT['NON']
            if any(is_key_active):
                rep += next_line
            itr += 1
        rep += "\n"
    for _, subdivisions in times.subdivisions.iteritems():
        for sub_times in subdivisions:
            rep += _report_itrs(sub_times, delim_mode)
    for _, par_subdivisions in times.par_subdivisions.iter_items():
        for _, par_list in par_subdivisions.iteritems():
            sub_with_max_tot = max(par_list, key=lambda x: x.total)
            rep += _report_itrs(sub_with_max_tot, delim_mode)
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


#
# Comparing / Parallel Reporting.
#


#
# Assemble times data.
#


def _build_master(master, times_list):
    num_times = len(times_list)
    for i, times in enumerate(times_list):
        _build_master_single(master, times, i, num_times)


def _build_master_single(master, times, index, num_times):
        for stamp, val in times.stamps.cum.iteritems():
            if stamp not in master.stamps:
                master.stamps[stamp] = [''] * num_times
            master.stamps[stamp][index] = val
        for stamp, sub_list in times.subdivisions:
            if stamp not in master.subdivisions:
                master.subdivisions[stamp] = list()
            for sub_times in sub_list:
                is_new = True
                for master_sub in master.subdivisions[stamp]:
                    if master_sub.name == sub_times.name:
                        is_new = False
                        break
                if is_new:
                    master_sub = CompareTimes(name=sub_times.name, parent=master)
                    master.subdivisions[stamp].append(master_sub)
                _build_master_single(master_sub, sub_times, index, num_times)
        for stamp, par_dict in times.par_subdivisions.iteritems():
            if stamp not in master.par_subdivisions:
                master.par_subdivisions[stamp] = dict()
            for par_name, par_list in par_dict.iteritems():
                if par_name not in master.par_subdivisions[stamp]:
                    master_sub = CompareTimes(name=par_name, parent=master)
                    master.par_subdivisions[stamp][par_name] = master_sub
                master_sub = master.par_subdivisions[stamp][par_name]
                sub_with_max_tot = max(par_list, key=lambda x: x.total)
                _build_master_single(master_sub, sub_with_max_tot, index, num_times)


class CompareTimes(object):

    def __init__(self, name=None, parent=None):
        self.name = str(name)
        self.parent = parent
        self.stamps = dict()
        self.stats = dict()
        self.subdivisions = dict()
        self.par_subdivisions = dict()


class StampStats(object):

    def __init__(self):
        self.num = 0
        self.max = 0.
        self.min = 0.
        self.avg = 0.
        self.std = 0.


def _populate_compare_stats(master):
    for stamp, values in master.stamps.iteritems():
        master.stats[stamp] = _compute_stats(values)
    for _, sub_list in master.subdivisions.iteritems():
        for master_sub in sub_list:
            _populate_compare_stats(master_sub)
    for _, sub_dict in master.par_subdivisions.iteritems():
        for _, master_sub in sub_dict.iteritems():
            _populate_compare_stats(master_sub)


def _compute_stats(values):
    use_values = filter(lambda x: x != '' and x != 0, values)
    s = StampStats()
    s.num = len(use_values)
    if s.num > 0:
        s.max = max(use_values)
        s.min = min(use_values)
        s.avg = sum(use_values) / s.num
        s.std = pow(sum([(v - s.avg)**2 for v in use_values]) / s.num, 0.5)
    return s


#
# Writing Comparison Report
#


def _define_compare_formats(delim_mode, fmt_opts):
    global FMTS_CMP
    if not isinstance(fmt_opts, dict):
        raise TypeError("Expected dictionary for format_options input.")
    if delim_mode:
        DELIM = '\t' if 'delimiter' not in fmt_opts else str(fmt_opts['delimiter'])
        IDT_SYM = '+' if 'indent_symbol' not in fmt_opts else str(fmt_opts['indent_symbol'])
        NAME = "\n{{}}{}{{}}".format(DELIM)  # accepts: indent, name
        NUM = "{}{{}}".format(DELIM)  # accepts: value
        CMPR = {
            'BEGIN': "Parallel / Comparison Report ({})\n",  # accepts: par_name?
            'NONE': "\n(Neither list nor stats selected for reporting.)\n",
            'END': "\nEnd Parallel / Comparison Report"
        }
        LIST = {
            'HDR': NUM,
            'NAME': NAME,
            'NM_BNLK': DELIM,
            'NUM': NUM,
            'IDT_SYM': IDT_SYM,
            'APND': '',
            'BLNK': DELIM
        }
        STAT = LIST
    else:
        STMP_NAME = 20 if 'stamp_name_width' not in fmt_opts else int(fmt_opts['stamp_name_width'])
        LIST_COL = 20 if 'list_column_width' not in fmt_opts else int(fmt_opts['list_column_width'])
        LIST_TAB = 2 if 'list_tab_width' not in fmt_opts else int(fmt_opts['list_tab_width'])
        STAT_COL = 12 if 'stat_column_width' not in fmt_opts else int(fmt_opts['stat_column_width'])
        STAT_TAB = 2 if 'stat_tab_width' not in fmt_opts else int(fmt_opts['stat_tab_width'])
        IDT_SYM = '  ' if 'indent_symbol' not in fmt_opts else str(fmt_opts['indent_symbol'])
        HDR = "{0}{{:>{1}.{1}}}"
        NAME = "\n{{}}{{:.<{}}}".format(STMP_NAME)  # accepts: indent, name
        NUM = "{}{{:{}.2f}}"  # accepts: tab, column width
        BLNK = "{}{}"  # accepts: tab, column width
        CMPR = {
            'BEGIN': "\n\n---Parallel / Comparison Report ({})\n",  # accepts: par_name?
            'NONE': "\n(Neither list nor stats selected for reporting.)\n",
            'END': "\n---End Parallel / Comparison Report---\n"
        }
        LIST = {
            'HDR': HDR.format(' ' * LIST_TAB, LIST_COL),  # accepts: name
            'NAME': NAME,
            'NM_BLNK': "\n{}".format(' ' * STMP_NAME),
            'NUM': NUM.format(' ' * LIST_TAB, LIST_COL),  # accepts: value
            'IDT_SYM': IDT_SYM,
            'BLNK': BLNK.format(' ' * LIST_TAB, ' ' * LIST_COL),
            'APND': ' '
        }
        STAT = {
            'HDR': HDR.format(' ' * STAT_TAB, STAT_COL),  # accepts: name
            'NAME': NAME,
            'NM_BLNK': "\n{}".format(' ' * STMP_NAME),
            'NUM': NUM.format(' ' * STAT_TAB, STAT_COL),  # accepts: value
            'IDT_SYM': IDT_SYM,
            'BLNK': BLNK.format(' ' * STAT_TAB, ' ' * STAT_COL),
            'APND': ' '
        }
    FMTS_CMP = {'Compare': CMPR, 'List': LIST, 'Stats': STAT}


def _compare_stats(times_list, master, delim_mode):
    FMT = FMTS_CMP['Stats']
    rep = ''
    tot = _compute_stats([times.total for times in times_list])
    rep += FMT['NM_BLNK']
    headers = ['Max', 'Min', 'Mean', 'StDev', 'Num']
    for hdr in headers:
        rep += FMT['HDR'].format(hdr)
    if not delim_mode:
        rep += FMT['NM_BLNK']
        for _ in range(len(headers)):
            rep += FMT['HDR'].format('------')
    rep += FMT['NAME'].format('', 'Total' + FMT['APND'])
    values = [tot.max, tot.min, tot.avg, tot.std, tot.num]
    for val in values:
        rep += FMT['NUM'].format(val)
    rep += "\n\n"
    rep += _compare_stamp_stats(master)
    rep += "\n"
    return rep


def _compare_list(times_list, master, delim_mode):
    FMT = FMTS_CMP['LIST']
    rep = ''
    rep += FMT['NM_BLNK']
    for i in range(len(times_list)):
        rep += FMT['HDR'].format(i)
    rep += FMT['NM_BLNK']
    for times in times_list:
        rep += FMT['HDR'].format(times.name)
    rep += "\n"
    if not delim_mode:
        rep += FMT['NM_BLNK']
        for _ in range(len(times_list)):
            rep += FMT['HDR'].format('-------')
    rep += FMT['NAME'].format('', 'Total')
    for times in times_list:
        rep += FMT['NUM'].format(times.total)
    rep += "\n\n"
    rep += _compare_stamps(master)
    rep += "\n"
    return rep


def _compare_stamp_stats(master, indent=0):
    FMT = FMTS_CMP['Stats']
    rep = ''
    for stamp, s in master.stats.iteritems():
        rep += FMT['NAME'].format(FMT['IDT_SYM'] * indent, stamp + FMT['APND'])
        values = [s.max, s.min, s.avg, s.std, s.num]
        for val in values:
            if val:
                rep += FMT['NUM'].format(val)
            else:
                rep += FMT['BLNK']
        if stamp in master.subdivisions:
            for master_sub in master.subdivisions[stamp]:
                rep += _compare_stamp_stats(master_sub, indent + 1)
        if stamp in master.par_subdivisions:
            for _, master_sub in master.par_subdivisions[stamp].iteritems():
                rep += _compare_stamp_stats(master_sub, indent + 1)
    return rep


def _compare_stamps(master, indent=0):
    FMT = FMTS_CMP['LIST']
    rep = ''
    for stamp, values in master.stamps.iteritems():
        rep += FMT['NAME'].format(FMT['IDT_SYM'] * indent, stamp + FMT['APND'])
        for val in values:
            if val:
                rep += FMT['NUM'].format(val)
            else:
                rep += FMT['BLNK']
        if stamp in master.subdivisions:
            for master_sub in master.subdivisions[stamp]:
                rep += _compare_stamps(master_sub)
        if stamp in master.par_subdivisions:
            for _, master_sub in master.par_subdivisions[stamp]:
                rep += _compare_stamps(master_sub)


#
#  Times Structure (not part of parallel / comparison).
#


def _write_structure(times, indent=0):
    strct = "\n{}{}".format(' ' * indent, times.name)
    if times.pos_in_parent:
        strct += " ({})".format(times.pos_in_parent)
    for _, sub_list in times.subdivisions.iteritems():
        for sub_times in sub_list:
            strct += _write_structure(sub_times, indent + 4)
    for _, par_dict in times.par_subdivisions.iteritems():
        for _, par_list in par_dict.iteritems():
            sub_with_max_tot = max(par_list, key=lambda x: x.total)
            strct += _write_structure(sub_with_max_tot, indent + 4)
    return strct
