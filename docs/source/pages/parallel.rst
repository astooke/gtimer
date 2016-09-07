Parallel Applications
=====================

When using gtimer in the context of parallel computing, with multiple separate python processes, each one will operate its own, independent gtimer.  Therefore it is necessary to communicate parallel subdivisions to the master timer more explicitly than in the case of serial operation.

One option is to explicitly pass timing data as any other results are retrieved from a sub-processes.  Use the ``get_times()`` function to retrieve a deepcopy of the timing data.

Another option is to use the ``save_pkl()`` and ``load_pkl()`` methods.  The first of these gets, pickles, and returns the current timing data if no arguments are provided, or else it can pickle a given ``Times`` instance and / or dump to a provided filename.

Once the master process timer holds a collection of ``Times`` objects containing data from a completed sub-processes, they can be attached to the hierarchy using ``attach_par_subdivision()``.  The attached timing data will exist in a temporary state until the next ``stamp()`` call in the master timer, at which point the data will be permanently assigned to the master timer hierarchy, just as a regular subdivision ended during that interval is.  To summarize, the proper sequence is:

1. stamp in master
2. run subprocesses
3. get times from subprocesses
4. attach times to master
5. stamp in master.  

To stamp in the master during a sub-process run (between steps 2-4), first subdivide within the master, and end that subdivision before attaching.

In a setting with a flat hierarchy of workers operating from beginning to end, timing data can be held separately until program execution is complete, and then the times data collected into a list for side-by-side comparison.

Specifically in multiprocessing, it is possible that a spawned child process will inherit unwanted timing data from the master process.  In this case, inside the sub-process, initialize with a call to ``reset_root()``, which wipes the history clean by instantiating a new underlying data structure.  Persistent parallel workers with repeated task assignments could also ``reset()`` or ``reset_root()`` at the beginning of each task assignement, to export only new timing data each time.

IMPORTANT: All timers from sub-processes attached repeatedly in a loop must be given distinct root names (within sub-process, e.g.: ``rename_root_timer(worker_id)``).  Timers with matching names assigned to the same position and same parallel group name will be interpreted as coming from successive iterations of the same source and will have data incorrectly merged together, possibly in an undefined fashion.  The parallel group name should be descriptive but the inidividual timer names could simply be the process number (will be converted via ``str()``).

In the future, it is hoped to incorporate a standalone memory-mapping solution for sharing data between processes without having to alter the signature of the parallel call and without having to reach to disk.
