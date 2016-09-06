
Stamp Settings
==============

Four different settings affect the behavior of calls to ``stamp()``, as described here.


1. Unique
---------

Checks whether the stamp name has been used previously in the current level in timer hierarchy, and raises ``UniqueNameError`` if so.  When inside a timed loop, gtimer will raise the exception if ever the same stamp name is encountered twice in one iteration.  Disjoint segments of code within a timed loop can be assigned to the same stamp name using ``unique=False``, and the iteration data will still count according to loop iteration.

Keyword args: ``unique`` or ``un``

Default: ``True``


2. Keep Subdivisions
--------------------

Decide whether to keep timing subdivisions which have occured since the previous stamp (each subdivision is permanently affixed to its parent timer at the first stamp call following closure of the subdivision).  Perhaps a deeply nested subfunction call is not of interest for a particular run; this option can be used to ignore unwanted data without having to dig.

Keyword args: ``keep_subdivisions`` or ``ks`` 

Default: ``True`` for ``stamp()``, ``False`` for ``b_stamp()`` (only option active for ``b_stamp()``)


3. Quick Print
--------------

One way to observe timing in progress; prints one line with the name and elapsed time newly assigned to the stamp (or total time at ``stop()``).

Keyword args: ``quick_print`` or ``qp``

Default: ``False``


4. Save Iterations
------------------

Decide whether to save timing data for every iteration of each stamp, or else only the statistics (max, min, etc.).  This setting is not applied to individual stamps, but to whole loops or subdivisions (named loops may be an exception).  Set using the keyword arg ``save_itrs`` to the ``timed_loop()`` and ``timed_for()`` constructors.  This keyword is also an optional argument to ``wrap()`` and ``subdivide()``.  In these cases, when a subfunction is called multiple times, it may not "know" that it is an iteration each time, but as timing data is accumulated, gtimer can still save individual iteration data according to this flag.  This setting applies immediately to the level at which it is applied, and does not propagate down the hierarchy (e.g. you can save iterations of an inner loop without doing so for the outer loop, but you must specify everywhere you want to deviate from the default behavior).

Default: ``True``


Global Defaults
---------------

All of these settings can have their default set at any place in the code, affecting subsequent calls, using the ``set_def_xx()`` commands (e.g. ``set_def_unique(True)``).  This is active for wrapped functions--a wrapper with no ``save_itrs`` arg defines the behavior to query the current default setting at function entrance.  The ``b_stamp()`` method is not subject to these settings; its default setting ``keep_subdivisions=False`` can be overridden individually but is otherwise hard-coded.


Long-form vs Short-form Keywords
--------------------------------

The long-form and short-form variations of the keywords provided are equivalent.  If either or both are present, the global default is ignored and the keywords are OR'ed together (individual keyword default is ``None``).
