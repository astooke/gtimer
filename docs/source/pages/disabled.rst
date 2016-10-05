
Disabled Mode
=============

G-Timer can be fully disabled by setting the environment variable 'GTIMER_DISABLE' to any value other than '0', before the first import of G-Timer.  All functions will keep the same signature, but most will simply pass.  Timed loops will still function, as bare loops.  The status is recorded in the ``gtimer.DISABLED`` variable.  To reenable, change the environment variable and reload gtimer.
