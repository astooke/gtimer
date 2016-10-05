Parallel Applications
=====================

When using G-Timer in the context of parallel computing, with multiple separate python processes, each one will operate its own, independent G-Timer.  Therefore it may be necessary to communicate parallel timing data to the master timer.

Communicating Raw Times
-----------------------

One parallel tool is the option to backdate in the ``stamp()`` function.  This receives a time and applies a stamp in the current timer as if it happened at that time (the backdate time must be in the past but more recent than the latest stamp).  A sub-process can return a time or a collection of times to the master process, so that the master need not synchronously monitor sub-process status.  The effect is that timing data from a sub-process appears as if native in the master.

Communicating ``Times`` Objects
-------------------------------

It is also possible to send ``Times`` data objects from sub-processes to the master and incorporate them into the master timer as subdivisions.  This can be done using the ``get_times()`` function or ``save_pkl()`` for a serialized version.  Disk storage could be utilized with ``load_pkl()``.

Once the master process holds a collection of ``Times`` objects from completed sub-processes, they can be attached to the hierarchy using ``attach_par_subdivision()``.  In case timing data from only one representative worker is sufficient, ``attach_subdivision()`` can be used on a single ``Times`` object.  In either case, the attached timing data will exist in a temporary state until the next ``stamp()`` call in the master timer, at which point the data will be permanently assigned to the master timer hierarchy, just as a regular subdivision ended during that interval is.  To summarize, the proper sequence is:

1. stamp in master
2. run subprocesses
3. get times from subprocesses
4. attach times to master
5. stamp in master.

To stamp in the master during a sub-process run (between steps 2-4), it is recommended to first subdivide within the master, and end that subdivision before attaching.  Otherwise, the master stamp containing the parallel subdivision will not reflect the duration of the parallel work.

The ``compare()`` function can be used to examine parallel subdivisions held within a single timer.

IMPORTANT: All timers from different sub-processes attached repeatedly as parallel subdivisions must be given distinct root names (within sub-process, e.g.: ``rename_root_timer(worker_id)``).  Timers with matching names assigned to the same position and same parallel group name will be interpreted as coming from successive iterations of the same source and will have data incorrectly merged together, possibly in an undefined fashion.  The parallel group name should be descriptive but the inidividual timer names could simply be the process number (will be converted via ``str()``).  When attaching only one representative in a loop, use the same timer name every time, regardless if the source sub-process changes.

In the future, it is hoped to incorporate a standalone memory-mapping solution for sharing data between processes without having to alter the signature of the parallel call and without having to reach to disk.

Independent Timing
------------------
Yet another option is to wait until program completion to collect the timing data from parallel workers to a central holding place.  Then a side-by-side comparison can be reported using ``compare()``.


Process Inheritance
-------------------

Specifically in multiprocessing, it is possible that a spawned child process will inherit unwanted timing data from the master process.  Use ``reset_root()`` to clear the history and instantiate a new underlying data structure.  Persistent parallel workers with repeated task assignments could also ``reset()`` or ``reset_root()`` at the beginning of each task assignement, to export only new timing data at desired intervals.



