
"""
Internal functions for managing times data objects.
"""
from __future__ import absolute_import
from timeit import default_timer as timer

from gtimer.private import focus as f
from gtimer.local import merge
from gtimer.util import iteritems, itervalues


#
# Functions to expose elsewhere in the package.
#


def dump_times():
    f.r.total = f.t.tmp_total - f.r.self_agg  # (have already subtracted self_cut)
    f.r.stamps_sum = sum([v for v in itervalues(f.s.cum)])
    f.r.self_agg += f.t.self_cut  # (now add self_cut including self time of stop())
    if f.s.itrs:
        for s, itr_list in iteritems(f.s.itrs):
            f.s.itr_max[s] = max(itr_list)
            nonzero_itrs = list(filter(lambda x: x > 0., itr_list))
            f.s.itr_num[s] = len(nonzero_itrs)
            if f.s.itr_num[s] > 0:
                f.s.itr_min[s] = min(nonzero_itrs)
            else:
                f.s.itr_min[s] = 0.
    for s, val in iteritems(f.s.cum):  # (for saving stamps_as_itr)
        if s not in f.s.itr_num:
            f.s.itr_num[s] = 1
            f.s.itr_max[s] = val
            f.s.itr_min[s] = val
    merge_t = 0.
    if f.t.dump is not None:
        t = timer()
        merge.merge_times(f.t.dump, f.r)
        merge_t += timer() - t
        f.t.dump.self_agg += merge_t
    # Must aggregate up self time only in the case of named loop, because it
    # dumps directly to an already assigned subdivision, whereas normally self
    # time aggregates during subdivision assignment.
    if f.t.is_named_loop:
        f.r.parent.self_agg += f.r.self_agg + merge_t


def assign_subdivisions(position, keep_subdivisions=True):
    # Aggregate the self-time whether subdvisions kept or not.
    for times in itervalues(f.t.subdvsn_awaiting):
        f.r.self_agg += times.self_agg
    for sub_list in itervalues(f.t.par_subdvsn_awaiting):
        sub_with_max_tot = max(sub_list, key=lambda x: x.total)
        f.r.self_agg += sub_with_max_tot.self_agg
    if keep_subdivisions:
        if f.t.subdvsn_awaiting:
            _assign_subdvsn(position)
        if f.t.par_subdvsn_awaiting:
            _assign_par_subdvsn(position)
    f.t.subdvsn_awaiting.clear()
    f.t.par_subdvsn_awaiting.clear()


#
# Private helper functions.
#


def _assign_subdvsn(position):
    new_pos = position not in f.r.subdvsn and f.t.subdvsn_awaiting
    if new_pos:
        f.r.subdvsn[position] = list()
        for sub_times in itervalues(f.t.subdvsn_awaiting):
            sub_times.pos_in_parent = position
            f.r.subdvsn[position] += [sub_times]
    else:
        for sub_times in itervalues(f.t.subdvsn_awaiting):
            is_prev_sub = False
            for old_sub in f.r.subdvsn[position]:
                if old_sub.name == sub_times.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                merge.merge_times(old_sub, sub_times)
            else:
                sub_times.pos_in_parent = position
                f.r.subdvsn[position].append(sub_times)


def _assign_par_subdvsn(position):
    new_pos = position not in f.r.par_subdvsn and f.t.par_subdvsn_awaiting
    if new_pos:
        f.r.par_subdvsn[position] = dict()
        for par_name, sub_list in iteritems(f.t.par_subdvsn_awaiting):
            for sub_times in sub_list:
                sub_times.pos_in_parent = position
            f.r.par_subdvsn[position][par_name] = sub_list
    else:
        for par_name, sub_list in iteritems(f.t.par_subdvsn_awaiting):
            if par_name not in f.r.par_subdvsn[position]:
                for sub_times in sub_list:
                    sub_times.pos_in_parent = position
                f.r.par_subdvsn[position][par_name] = sub_list
            else:
                for sub_times in sub_list:
                    is_prev_sub = False
                    for old_sub in f.r.par_subdvsn[position][par_name]:
                        if old_sub.name == sub_times.name:
                            is_prev_sub = True
                            break
                    if is_prev_sub:
                        merge.merge_times(old_sub, sub_times)
                    else:
                        sub_times.pos_in_parent = position
                        f.r.par_subdvsn[position][par_name].append(sub_times)
