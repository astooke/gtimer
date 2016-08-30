
import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True

if DISABLED:
    from disabled_pub import *
else:
    from timer_glob import *
    from loop import *
    from mgmt_pub import *
    from report_glob import *
