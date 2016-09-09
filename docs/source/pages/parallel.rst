Parallel Applications
=====================

When using gtimer in the context of parallel computing, with multiple separate python processes, each one will operate its own, independent gtimer.  Therefore it is necessary to communicate parallel timing data to the master timer.

Communicating Raw Times
-----------------------

One parallel tool is the function ``backdate_stamp()``.  This receives a time and applies a stamp in the current timer as if it happened at that time (the backdate time must be in the past but more recent than the last stamp).  A sub-process can return a time (e.g. returned from any gtimer timing action) or a collection of times to the master process, so that the master need not synchronously monitor sub-process status.

Communicating ``Times`` Objects
-------------------------------

Another option is to send ``Times`` data objects from sub-processes to the master.  This can be done using the ``get_times()`` function or ``save_pkl()`` for a serialized version.  Disk storage could be utilized with ``load_pkl()``.  

Once the master process holds a collection of ``Times`` objects from completed sub-processes, they can be attached to the hierarchy using ``attach_par_subdivision()``.  The attached timing data will exist in a temporary state until the next ``stamp()`` call in the master timer, at which point the data will be permanently assigned to the master timer hierarchy, just as a regular subdivision ended during that interval is.  To summarize, the proper sequence is:

1. stamp in master
2. run subprocesses
3. get times from subprocesses
4. attach times to master
5. stamp in master.  

To stamp in the master during a sub-process run (between steps 2-4), it is recommended to first subdivide within the master, and end that subdivision before attaching.  Otherwise, the master stamp containing the parallel subdivision will not reflect the duration of the parallel work.

In a setting with a flat hierarchy of workers operating from beginning to end, timing data can be held separately until program execution is complete, and then the times data collected into a list for side-by-side comparison.  The ``compare()`` function can also be used to examine parallel subdivisions held within a single timer.

IMPORTANT: All timers from sub-processes attached repeatedly in a loop must be given distinct root names (within sub-process, e.g.: ``rename_root_timer(worker_id)``).  Timers with matching names assigned to the same position and same parallel group name will be interpreted as coming from successive iterations of the same source and will have data incorrectly merged together, possibly in an undefined fashion.  The parallel group name should be descriptive but the inidividual timer names could simply be the process number (will be converted via ``str()``).

In the future, it is hoped to incorporate a standalone memory-mapping solution for sharing data between processes without having to alter the signature of the parallel call and without having to reach to disk.


Process Inheritance
-------------------

Specifically in multiprocessing, it is possible that a spawned child process will inherit unwanted timing data from the master process.  Use ``reset_root()`` to clear the history and instantiate a new underlying data structure.  Persistent parallel workers with repeated task assignments could also ``reset()`` or ``reset_root()`` at the beginning of each task assignement, to export only new timing data at desired intervals.



