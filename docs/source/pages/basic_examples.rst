
Basic Examples
==============

Subdividing
-----------

.. literalinclude:: /examples/example_1.py

.. literalinclude:: /examples/result_1.txt

A call to ``stamp()`` marks the end of an interval, and it always applies to the current level in the timer hierarchy.  The time in the ``func_1`` subdivision (induced by the decorator) was accumulated entirely within the span of the interval ``'first'`` in the root timer.  The negligible time associated with the stamp ``'second'`` resulted from in-line timing of the un-decorated ``func_2``.

Using the ``quick_print`` flag in a stamp prints the elapsed interval time immediately.

The "Self Time" is how long was spent inside gtimer, and has already been subtracted from the total.  All times are always presented in units of seconds.  (The default base timer name is "root".)

IMPORTANT: Subdivisions are managed according to their names.  Two separate subdivisions of the same name, occuring at the same level and between stamps in the surrounding timer, will be counted as two iterations of the same timer and their data merged.  If this is not the intended outcome, use distinct names.


Timer Control
-------------

.. literalinclude:: /examples/example_2.py
   :lines: 4-  

.. literalinclude:: /examples/result_2.txt

Calling ``start()`` ignores any previous time, the time between ``pause()`` and ``resume()`` are ignored, and so is any time after ``stop()`` (used here with an optional stamp name).  The function ``b_stamp()`` begins a new interval but discards the time data of the one it ends.  There is finality in the ``stop()`` command--afterwords a timer level cannot be resumed but can be reset.

The "Stamps Sum" field indicates that the stamps data is not all-inclusive of the total time, due to the ``b_stamp()`` call.  This can also happen if stopping without stamping, or if no stamp is called immediately prior to enterting a timed loop.


Comparing Results
-----------------

Use the ``get_times()`` function (or ``save_pkl()``, ``load_pkl()``) at the end of a completed timed run to retrieve the timing data.  Collect results from multiple runs into a list and provide it to the ``compare()`` function to return a side-by-side comparison of timing data.  For example, in an interactive session:

.. code-block:: python

    run example.py
    gt.rename_root('run_1')
    times_1 = gt.get_times()
    run example.py
    gt.rename_root('run_2')
    times_2 = gt.get_times()
    print gt.compare([times_1, times_2])

    # inside example.py main:
    gt.reset_root()
    <body of script>
    gt.stop()


.. literalinclude:: /examples/compare.txt