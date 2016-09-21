
"""
Functions provided to user for saving / loading / combining times data objects.
"""
from __future__ import absolute_import
from timeit import default_timer as timer
try:
    import cPickle as pickle
except:
    import pickle
import copy
# import mmap
# import os

from gtimer.private import focus as f
from gtimer.private import collapse
from gtimer.local.times import Times
from gtimer.local import merge

__all__ = ['get_times', 'attach_subdivision', 'attach_par_subdivision',
           'save_pkl', 'load_pkl']
#          'open_mmap', 'close_mmap', 'save_mmap', 'load_mmap']


def get_times():
    """
    Produce a deepcopy of the current timing data (no risk of interference
    with active timing or other operaitons).

    Returns:
        Times: gtimer timing data structure object.
    """
    if f.root.stopped:
        return copy.deepcopy(f.root.times)
    else:
        t = timer()
        times = collapse.collapse_times()
        f.root.self_cut += timer() - t
        return times


def attach_par_subdivision(par_name, par_times):
    """
    Manual assignment of a collection of (stopped) Times objects as a parallel
    subdivision of a running timer.

    Notes:
        An example sequence of proper usage:

            1. Stamp in master process.
            2. Run timed sub-processes.
            3. Get timing data from sub-processes into master.
            4. Attach timing data (i.e. list of Times objects) in master using this method.
            5. Stamp in master process.

        To stamp in the master between steps 1 and 5, it is recommended to
        subdivide() between steps 1 and 2, and end that subdivision before
        attaching, or else the master stamp will not reflect the sub-process
        time.

    Args:
        par_name (any): Identifier for the collection, passed through str()
        par_times (list or tuple): Collection of Times data objects.

    Raises:
        TypeError: If par_times not a list or tuple of Times data objects.
    """
    t = timer()
    if not isinstance(par_times, (list, tuple)):
        raise TypeError("Expected list or tuple for param 'par_times'.")
    for times in par_times:
        if not isinstance(times, Times):
            raise TypeError("Expected each element of param 'par_times' to be Times object.")
        assert times.total > 0., "An attached par subdivision has total time 0, appears empty."
    par_name = str(par_name)
    sub_with_max_tot = max(par_times, key=lambda x: x.total)
    f.r.self_agg += sub_with_max_tot.self_agg
    if par_name not in f.t.par_subdvsn_awaiting:
        f.t.par_subdvsn_awaiting[par_name] = []
        for times in par_times:
            times_copy = copy.deepcopy(times)
            times_copy.parent = f.r
            times_copy.par_in_parent = par_name
            f.t.par_subdvsn_awaiting[par_name].append(times_copy)
    else:
        for new_sub in par_times:
            is_prev_sub = False
            for old_sub in f.t.par_subdvsn_awaiting[par_name]:
                if old_sub.name == new_sub.name:
                    is_prev_sub = True
                    break
            if is_prev_sub:
                merge.merge_times(old_sub, new_sub)
            else:
                new_sub_copy = copy.deepcopy(new_sub)
                new_sub_copy.parent = f.r
                new_sub_copy.par_in_parent = par_name
                f.t.par_subdvsn_awaiting[par_name].append(new_sub_copy)
    f.t.self_cut += timer() - t


def attach_subdivision(times):
    """
    Manual assignment of a (stopped) times object as a subdivision of running
    timer.  Use cases are expected to be very limited (mainly provided as a
    one-Times variant of attach_par_subdivision).

    Notes:
        As with any subdivision, the interval in the receiving timer is assumed to
        totally subsume the time accumulated within the attached object--the total
        in the receiver is not adjusted!

    Args:
        times (Times): Individual Times data object.

    Raises:
        TypeError: If times not a Times data object.
    """
    t = timer()
    if not isinstance(times, Times):
        raise TypeError("Expected Times object for param 'times'.")
    assert times.total > 0., "Attached subdivision has total time 0, appears empty."
    name = times.name
    f.r.self_agg += times.self_agg
    if name not in f.t.subdvsn_awaiting:
        times_copy = copy.deepcopy(times)
        times_copy.parent = f.r
        f.t.subdvsn_awaiting[name] = times_copy
    else:
        merge.merge_times(f.t.subdvsn_awaiting[name], times)
    f.t.self_cut += timer() - t


def save_pkl(filename=None, times=None):
    """
    Serialize and / or save a Times data object using pickle (cPickle).

    Args:
        filename (None, optional): Filename to dump to. If not provided,
            returns serialized object.
        times (None, optional): object to dump.  If non provided, uses
            current root.

    Returns:
        pkl: Pickled Times data object, only if no filename provided.

    Raises:
        TypeError: If 'times' is not a Times object or a list of tuple of
            them.
    """
    if times is None:
        if not f.root.stopped:
            times = collapse.collapse_times()
        else:
            times = f.root.times
    else:
        if isinstance(times, (list, tuple)):
            for t in times:
                if not isinstance(t, Times):
                    raise TypeError("Expected single Times instance or list/tuple of Times instances for param 'times'.")
        elif not isinstance(times, Times):
            raise TypeError("Expected single Times instance or list/tuple of Times instances for param 'times'.")
    if filename is not None:
        with open(str(filename), 'wb') as file:
            pickle.dump(times, file)
    else:
        return pickle.dumps(times)


def load_pkl(filenames):
    """
    Unpickle file contents.

    Args:
        filenames (str): Can be one or a list or tuple of filenames to retrieve.

    Returns:
        Times: A single object, or from a collection of filenames, a list of Times objects.

    Raises:
        TypeError: If any loaded object is not a Times object.
    """
    if not isinstance(filenames, (list, tuple)):
        filenames = [filenames]
    times = []
    for name in filenames:
        name = str(name)
        with open(name, 'rb') as file:
            loaded_obj = pickle.load(file)
            if not isinstance(loaded_obj, Times):
                raise TypeError("At least one loaded object is not a Times data object.")
            times.append(pickle.load(file))
    return times if len(times) > 1 else times[0]


#
# These are still under construction...not tested and probably not functional:
#

# def open_mmap(filenames, init_size=10000, write=True):
#     """
#     EXPERIMENTAL: UNTESTED OR NOT FUNCTIONING.

#     Args:
#         filenames (TYPE): Description
#         init_size (int, optional): Description
#         write (bool, optional): Description
#     """
#     if not isinstance(filenames, (list, tuple)):
#         filenames = [filenames]
#     files = list()
#     mmaps = list()
#     for name in filenames:
#         name = str(name)
#         if not os.path.isfile(name):
#             with open(name, 'w') as f:
#                 f.write(init_size * b'\0')
#         if write:
#             access = mmap.ACCESS_COPY
#         else:
#             access = mmap.ACCESS_READ
#         file = open(name, 'r+')
#         mm = mmap.mmap(f.fileno(), 0, access=access)
#         files.append(file)
#         mmaps.append(mm)
#     if len(files) > 1:
#         return files, mmaps
#     else:
#         return file, mm


# def close_mmap(mmaps, files):
#     """
#     EXPERIMENTAL: UNTESTED OR NOT FUNCTIONING.

#     Args:
#         mmaps (TYPE): Description
#         files (TYPE): Description
#     """
#     mmaps = list(mmaps)
#     files = list(files)
#     for mm in mmaps:
#         mm.close()
#     for file in files:
#         file.close()


# def save_mmap(mm, file, times=None):
#     """
#     EXPERIMENTAL: UNTESTED OR NOT FUNCTIONING.

#     Args:
#         mm (TYPE): Description
#         file (TYPE): Description
#         times (None, optional): Description
#     """
#     if times is not None:
#         assert isinstance(times, Times), "Input 'times' must be None or Times object."
#     times_pkl = save_pkl(times)
#     filesize = mm.size()
#     data_len = len(times_pkl)
#     if data_len > filesize:
#         mm.close()
#         file.seek(0, 2)
#         file.write((data_len - filesize) * b'\0')
#         mm = mmap.mmap(file.fileno(), data_len, access=mmap.ACCESS_COPY)
#     mm.seek(0)
#     mm.write(times_pkl)
#     return mm, data_len


# def load_mmap(mmaps, files, write=False):
#     """
#     EXPERIMENTAL: UNTESTED OR NOT FUNCTIONING.

#     Args:
#         mmaps (TYPE): Description
#         files (TYPE): Description
#         write (bool, optional): Description
#     """
#     mmaps = list(mmaps)
#     files = list(files)
#     times = list()
#     if write:
#         access = mmap.ACCESS_COPY
#     else:
#         access = mmap.ACCESS_READ
#     mmaps_new = list()
#     for file, mm in zip(files, mmaps):
#         size = os.path.getsize(f)
#         if size > mm.size():
#             mm.close()
#             mm_new = mmap.mmap(file.fileno(), 0, access=access)
#             mmaps_new.append(mm_new)
#             mm_new.seek(0)
#             times.append(pickle.loads(mm_new.read(size)))
#         else:
#             mmaps_new.append(mm)
#             mm.seek(0)
#             times.append(pickle.loads(mm.read(size)))
#     if len(times) > 1:
#         return times, mmaps_new
#     else:
#         return times[0], mmaps_new[0]
