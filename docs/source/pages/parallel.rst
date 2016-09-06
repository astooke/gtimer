Parallel Considerations
=======================

When using gtimer in the context of parallel computing, with multiple separate python processes, it is necessary to communicate parallel subdivisions to the master timer more explicitly than in the case of serial operation.  Here we consider options when using multiprocessing, which makes options for MPI-type usage clear.

One option is to explicitly pass timing data as any other results are returned from sub-processes.  Use the ``get_times()`` method to retrieve a copy (a deepcopy--no risk of interfereing with active timing or other usage) of the timing data (in a ``Times`` object) and return that.

Another option is to use the ``save_pkl()`` and ``load_pkl()`` methods.  The first of these gets, pickles, and returns the current timing data if no arguments are provided, or else it can pickle a given ``Times`` instance and / or dump to a provided filename.

Once the master timer holds a ``Times`` object containing data from a completed sub-process, it can be attached to the hierarchy using ``attach_subdivision()`` (for just one) or ``attach_par_subdivision()`` for a list or tuple of results from multiple sub-processes.  Some care is necessary here, for gtimer cannot automatically deduce the right data hierarchy.  The attached timing data will exist in a temporary state until the next ``stamp()`` call in the master timer, at which point the data will be permanently assigned to the master timer hierarchy just as a regular subdivision ended during that interval is.  To summarize, the proper sequence is: 1. stamp in master, 2. run subprocesses, 3. get times from subprocesses, 4. attach times to master, 5. stamp in master.  To stamp in the master during a sub-process run (between steps 2-4), first subdivide within the master, and end that subdivision before attaching.

In a setting with a flat hierarchy of workers operating from beginning to end, timing data can be held separately until program execution is complete, and then the times data collected into a list for side-by-side comparison.

ALL TIMERS FROM SUB-PROCESSES ATTACHED REPEATEDLY IN A LOOP MUST BE GIVEN DISTINCT ROOT NAMES (within sub-process: ``rename_root_timer(worker_id)``).  Timers with matching names assigned to the same position and same parallel group name will be interpreted as coming from successive iterations of the same source and will have data incorrectly merged together, possibly in an undefined fashion.  For example the parallel group name should be descriptive and the inidividual timer names could simply be process number (will be converted via ``str()``).

Specifically in regards to multiprocessing, it is possible that a spawned child process will inherit unwanted timing data from the master process.  In this case, inside the sub-process, initialize with a call to ``hard_reset()``, which wipes the history clean by creating a new underlying data structure.  Persistent parallel workers with repeated task assignments could also ``reset()`` or ``hard_reset()`` at the beginning of each task assignement, to export only new timing data each time.

In the future, it is hoped to incorporate a standalone memory-mapping solution for sharing data between processes without having to alter the signature of the parallel call and without having to reach to disk.
