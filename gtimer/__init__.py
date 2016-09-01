
import os

DISABLED = False
if 'GTIMER_DISABLE' in os.environ:
    if os.environ['GTIMER_DISABLE'] != '0':
        DISABLED = True


if not DISABLED:
    from timer_glob import *
    from loop import *
    from mgmt_pub import *
    from report_glob import *
    from file_io import *
else:
    from disabled_pub import *
