
Installation & Basic Examples
=============================

Installation
------------

Installation using PyPI and pip is standard::

    pip install gtimer


To view the source code and / or install::

    git clone https://github.com/astooke/gtimer
    cd gtimer
    pip install .

No third-party dependencies are required.


Example 1 - Stamping
--------------------

In this example we measure straight-line code, introducing the ``stamp()`` method, which measures the time since the previous ``stamp()`` call and requires a unique name.  Importing gtimer starts it automatically.   The ``report()`` command provides a formatted string for human-readable results.

.. literalinclude:: /examples/example_1.py


.. literalinclude:: /examples/result_1.txt


The total time is presented, as well as each interval.  Naturally, a call to ``stamp()`` marks the end of an interval.  The "Self Time" field measures how long was spent inside gtimer itself, and has already been subtracted from the total.  All times are always presented in units of seconds. From here on the import statements are implied in the examples.  (The default base timer name is "root".)


Example 2 - Subdividing
-----------------------

This example shows two ways to induce timer hierarchy, through the ``subdivide()`` method and the function decorator ``wrap()``.

.. literalinclude:: /examples/example_2.py
   :lines: 4-

.. literalinclude:: /examples/result_2.txt

The same ``stamp()`` command is used everywhere, and gtimer automatically applies the effect to the then-current level in the timing hierarchy.  The hierarchy is portrayed in the indentations in the interval names and durations.  For example, ``f_first`` and ``f_second``, came from ``func_1`` and are subdivisions of interval ``'first'``, meaning their times accumulated entirely within its scope.  The same functionality as ``wrap()`` is provided for inline code using ``subdivide()`` and ``end_subdivision()``, which can keep clutter out of higher level measurements.  The negligible time associated with the stamp ``second`` resulted from the choice not to wrap ``func_2``, so its timing information is recorded as if its contents were inlined with the calling script.  The functions ``func_1`` and ``func_2`` can be defined in separate files from the main script; simply importing gtimer in each file leads to the same behavior as above.  Try making a subdivision within a subdivision, or two separate subdivisions between one pair of stamps in the parent timer, and print the results.

IMPORTANT: Subdivisions are managed according to their names.  Two separate subdivisions of the same name, occuring at the same level and between stamps in the surrounding timer, will be counted as two iterations of the same timer and their data merged.  If this is not the intended outcome, use distinct names.


Example 3 - Tailoring Attention
-------------------------------

Not every bit of code in a program is always of interest.  This example demonstrates some commands which can be used to tailor the scope of what is timed.

.. literalinclude:: /examples/example_3.py
   :lines: 4-  

.. literalinclude:: /examples/result_3.txt

Calling ``start()`` ignores any previous time, and must be called before any stamps or subdivisions are made (if some initialization code induces unwanted stamps or subdivisions, these can always be discarded using ``hard_reset()``).  The timer is not active between ``pause()`` and ``resume()`` pairs, as seen by the negligible time recorded in the stamp ``'second'``.  Time passing while paused is not added to the total.  A less obvious effect is that of the method ``b_stamp()``, which stands for "blank stamp".  Imagine that what happens between ``'second'`` and ``'third'`` is no longer of interest, but it is still desired to mark the beginning of the interval used for ``'fourth'``--it's as simple as appending ``b_`` to the front of ``stamp`` (it keeps the same signature--we can get it back later).  The name ``'third'`` is ignored and data clutter reduced in the report.  

There is finality in the ``stop()`` command.  A stopped timer cannot be resumed, but instead must be completely reset to begin timing again.  This example used an optional name argument to ``stop()``, which causes it to also perform a stamp.

The "Stamps Sum" field now indicates that the timing data captured by the stamps is not all-inclusive of the total time, due to the ``b_stamp()`` call.  This can also happen if you forget to (or choose not to) stamp at the end of a script or immediately prior to enterting a timed loop, covered in the next page.