
Loops
=====

Non-Unique Stamps
----------------------------------

.. literalinclude:: /examples/loop_1.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_1.txt

Setting the ``unique`` flag of a stamp to ``False`` allows it to accumulate time at every iteration.  Use of the ``unique`` flag also allows times from disjoint segments of code to be assigned to the same stamp name.  (In general, enforcing uniqueness helps prevent accidental mishandling of measurements--gtimer uses the names of stamps and timers as identifiers.)


Timed For
--------------------------

.. literalinclude:: /examples/loop_2.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_2.txt

The loop in this example is termed an "anonymous" loop, since the intervals within it are recorded flat in the hierarchy of the surrounding code.


Timed While
----------------------------

.. literalinclude:: /examples/loop_3.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_3.txt

The ``timed_loop()`` command returns a timed loop object which can be iterated using either the built-in ``next(loop)`` or ``loop.next()``.  Place this as the first line inside the loop.  At the first line past the loop, call ``loop.exit()`` to finish loop recording.  The optional name provided to the loop is used in two places: as a stamp name in the surrounding timer and as the timer name for a subdivision that exists only within the loop.  (In this case, with only one stamp inside the loop, that data is redundant.)


Timed Loop Details
------------------

``timed_loop()`` and ``timed_for()`` both return objects that can be used as context managers::

    with gt.timed_loop('named_loop') as loop:
        while x < 3:
            next(loop)
            do_unto_x()
            gt.stamp('loop')

When a ``timed_for`` loop used without context management needs to be broken, the loop's ``exit()`` must be called explicitly.  Redundant exits do no harm.  The ``timed_loop`` object can be used in both for and while loops.  

Each timed loop must use a new instance.  This means an inner loop object must be (re-)instantiated within the outer loop.  Due to name-checking, anonymous inner loops are not supported--all inner timed loops must be named (plain inner loops using non-unique stamps are OK).


Registered Stamps
^^^^^^^^^^^^^^^^^

Registering stamps (using the ``rgstr_stamps`` timed loop keyword) will cause a 0 to be listed in any iteration in which the stamp was not encountered.  This would change the report for ``loop_2`` in example 2.  The option to register stamps is also available for subdivisions, in case of conditional stamps in subfunctions called repeatedly.

