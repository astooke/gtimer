
Introductory Examples
=====================

Starting Simple
---------------

.. literalinclude:: /examples/example_0.py

.. literalinclude:: /examples/example_0.txt

The timer automatically starts on import, and each call to ``stamp()`` marks the end of an interval.  The "Self Time" is how long was spent inside gtimer functions, and has already been subtracted from the total.  Times are always presented in units of seconds.  The default timer name is "root", and it is indicated that this timer was still running (i.e. has not been stopped)--reports can be generated at any time without interfering with timing.

(Internally, all timing is performed using ``default_timer()`` imported from ``timeit``.)



Subdividing
-----------

.. literalinclude:: /examples/example_1.py

.. literalinclude:: /examples/result_1.txt

Calls to ``stamp()`` always apply to the current level in the timer hierarchy.  The time in the ``'sub'`` subdivision was accumulated entirely within the span of the interval ``'fourth'`` in the root timer.  Subdivisions may be nested to any level, and subdivided times appear indented beneath the stamp to which they belong.

The negligible time of the interval ``'second'`` resulted from in-line timing of the un-decorated ``func_2``.

Using the ``quick_print`` flag in a stamp prints the elapsed interval time immediately.

IMPORTANT: Subdivisions are managed according to their names.  Two separate subdivisions of the same name, occuring at the same level and between stamps in the surrounding timer, will be counted as two iterations of the same timer and their data merged.  If this is not the intended outcome, use distinct names.


Timer Control
-------------

.. literalinclude:: /examples/example_2.py
   :lines: 4-  

.. literalinclude:: /examples/result_2.txt

Calling ``start()`` ignores any previous time, the time between ``pause()`` and ``resume()`` is ignored, and so is any time after ``stop()`` (used here with an optional stamp name).  The function ``blank_stamp()`` begins a new interval but discards the time data of the one it ends.  There is finality in the ``stop()`` command--afterwords a timer level cannot be resumed, but it can be reset.

The "Stamps Sum" field indicates that the stamps data is not all-inclusive of the total time, due to the ``blank_stamp()`` call.  This can also happen if stopping without stamping, or if no stamp is called immediately prior to enterting a timed loop.


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