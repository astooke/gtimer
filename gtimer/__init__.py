
"""
The gtimer package is a Python timing tool intended for use cases ranging from
quick, one-time measurements to permanent integration for recording project
performance.  The main features include:

- Flexible levels of detail: lines, functions, programs, or any combination
- Automatic organization of timing data
- Easy deployment and adjustment of measurements
- Convenient output to human-readable format or spreadsheet

See http://gtimer.readthedocs.io for full documentation, including examples.
"""
from __future__ import absolute_import
import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True

if not DISABLED:
    from gtimer.public.timer import *
    from gtimer.public.timedloop import *
    from gtimer.public.io import *
    from gtimer.public.report import *
    del public, private, local, util
else:
    from gtimer.disabled.public import *
    del disabled, util

del os, absolute_import
