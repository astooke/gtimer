
import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True
del os

if not DISABLED:
    from gtimer.public.timer import *
    from gtimer.public.mgmt import *
    from gtimer.public.loop import *
    from gtimer.public.report import *
    from gtimer.public.file_io import *
    del public, private, local
else:
    from gtimer.disabled.public import *
    del disabled
