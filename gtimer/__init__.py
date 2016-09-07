
"""
Gtimer is a package providing Python code-timing capabilities intended for
uses ranging from short, quick checks to long-term measurements able to
cleanly persist within a code base.  The user writes interval-marking commands
throughout code to measure desired segments, and gtimer records the results.
Arbitrary organizational hierarchy of timing data is possible using
subdivisions; gtimer manages the organization automatically, building it into
the data structure on the fly.  As a result, the user can wield gtimer in a
linear fashion, regardless of timing complexity.  Loop iteration data can be
recorded.  Gtimer operates across functions and files (simply import it in
each file), and even provides capabilities for parallel computing.
Organizational structure and timing data are portrayed together in reports,
either human-readable or delimited.

See readthedocs..xx... for full documentation, including examples.
"""

import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True
del os

if not DISABLED:
    from gtimer.public.timer import *
    from gtimer.public.timedloop import *
    from gtimer.public.io import *
    from gtimer.public.report import *
    del public, private, local
else:
    from gtimer.disabled.public import *
    del disabled

# del util
