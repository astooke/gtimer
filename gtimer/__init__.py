
"""
gtimer overall docstring - TBD
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
