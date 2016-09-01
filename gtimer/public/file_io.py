
"""
Functions for saving / loading times data objects (exposed to user).
"""

import cPickle as pickle
import mmap
import os

from gtimer.private import glob as g
from gtimer.private import mgmt
from gtimer.local.times import Times

__all__  = ['save_pkl', 
            'load_pkl', 
            'open_mmap', 
            'close_mmap', 
            'save_mmap',
            'load_mmap',
            ]


def save_pkl(filename=None, times=None):
    if times is None:
        if not g.root_timer.stopped:
            times = mgmt.collapse_times()
        else:
            times = g.root_timer.times
    else:
        if not isinstance(times, Times):
            raise TypeError("Expected Times instance for times input.")
    if filename is not None:
        with open(str(filename), 'wb') as f:
            pickle.dump(times, f)
    else:
        return pickle.dumps(times)


def load_pkl(filenames):
    filenames = list(filenames)
    times = []
    for name in filenames:
        name = str(name)
        with open(name, 'rb') as f:
            times.append(pickle.load(f))
    return times if len(times) > 1 else times[0]


#
# These are still under construction...not tested:
#

def open_mmap(filenames, init_size=10000, write=True):
    filenames = list(filenames)
    files = list()
    mmaps = list()
    for name in filenames:
        name = str(name)
        if not os.path.isfile(name):
            with open(name, 'w') as f:
                f.write(init_size * b'\0')
        if write:
            access = mmap.ACCESS_COPY
        else:
            access = mmap.ACCESS_READ
        f = open(filename, 'r+')
        mm = mmap.mmap(f.fileno(), 0, access=access)
        files.append(f)
        mmaps.append(mm)
    if len(files) > 1:
        return files, mmaps
    else:
        return f, mm


def close_mmap(mmaps, files):
    mmaps = list(mmaps)
    files = list(files)
    for mm in mmaps:
        mm.close()
    for f in files:
        f.close()


def save_mmap(mm, file, times=None):
    if times is not None:
        assert isinstance(times, Times), "Input 'times' must be None or Times object."
    times_pkl = save_pkl(times)
    filesize = mm.size()
    data_len = len(times_pkl)
    if data_len > filesize:
        mm.close()
        file.seek(0, 2)
        file.write((data_len - filesize) * b'\0')
        mm = mmap.mmap(file.fileno(), data_len, access=mmap.ACCESS_COPY)
    mm.seek(0)
    mm.write(times_pkl)
    return mm, data_len


def load_mmap(mmaps, files, write=False):
    mmaps = list(mmaps)
    files = list(files)
    times = list()
    if write:
        access = mmap.ACCESS_COPY
    else:
        access = mmap.ACCESS_READ
    mmaps_new = list()
    for f, mm in zip(files, mmaps):
        size = os.path.getsize(f)
        if size > mm.size():
            mm.close()
            mm_new = mmap.mmap(f.fileno(), 0, access=access)
            mmaps_new.append(mm_new)
            mm_new.seek(0)
            times.append(pickle.loads(mm_new.read(size)))
        else:
            mmaps_new.append(mm)
            mm.seek(0)
            times.append(pickle.loads(mm.read(size)))
    if len(times) > 1:
        return times, mmaps_new
    else:
        return times[0], mmaps_new[0]
