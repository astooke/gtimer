
Loops
=====

Multiple loop measurement arrangements are possible in gtimer, which the following examples demonstrate.


Loop Example 1 - Non-Unique
---------------------------

The simplest approach is to disable the check for a unique stamp name within the loop.

.. literalinclude:: /examples/loop_1.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_1.txt

Setting the ``unique`` flag of the stamp to ``False`` allows it to accumulate time at every iteration.  Use of the ``unique`` flag also allows times from disjoint segments of code to be assigned to the same stamp name.  In general it is encouraged to keep uniqueness enforced, as in the following examples, since names play a central role as identifiers in timing hierarchies.


Loop Example 2 - Timed For
--------------------------

For more information, we can capture iteration data using gtimer's loop timing tools.  This example introduces ``timed_for()``.

.. literalinclude:: /examples/loop_2.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_2.txt

The report includes several iteration statistics and even a record of each individual iteration, if desired.  The only change to the code was replacing the plain iterable with gtimer's ``timed_for``, which accepts the iterable as its first agrument.  This loop is termed an "anonymous" loop, since the intervals within it are recorded flatly with the hierarchy with the surrounding code.  It is also possible to provide a name to the loop, in which case the loop is automatically subdivided, as in the following.


Loop Example 3 - Timed While
----------------------------

Support for while loops is included, as well, using the more general loop object returned by ``timed_loop()``. 

.. literalinclude:: /examples/loop_3.py
   :lines: 4-

.. literalinclude:: /examples/loop_result_3.txt

The ``timed_loop()`` command returns a timed loop object which can be iterated using either the built-in ``next()`` or a call directly to the object's method, as ``loop.next()``.  Place this as the first line inside the loop.  At the first line past the loop, call the ``loop.exit()`` method to finish loop recording.  The optional name provided to the loop is used in two places: as a stamp name in the surrounding timer, wherein iteration statistics are recorded, and as the timer name for a subdivision that exists only within the loop.  (In this case, with only one stamp inside the loop, the information is redundant.)


Loop Objects
------------

The loop object can be used as a context manager as in the following code equivalent to the last example, but where no explicit ``exit()`` call is required::

    with gt.timed_loop('named_loop') as loop:
        while x < 3:
            next(loop)
            do_unto_x()
            gt.stamp('loop')

In fact ``timed_loop`` and ``timed_for`` both return gtimer timed loop objects and can be used as context managers.  In the case of ``timed_for`` only, the loop object can also be used as the target iterable of a for loop, in which case the loop timing mode is automatically exited at the end of iteration.  One catch is that whenever a ``timed_for`` loop not used as a context manager is to be broken, a separate call to exit the loop must be made.  It is impossible for gtimer to notice and alert the user when execution leaves a timed loop block without properly exiting the timed loop object.  Redundant calls to exit a loop do no harm.    (The difference between the two is that ``timed_loop`` implements functionality in the ``next()`` or ``__next__()`` method, whereas ``timed_for`` holds functionality in its ``__iter__()`` method.)  A ``timed_loop`` object can just as well be used in a for loop as in a while loop.

In any case, each loop must use a separate timed loop instance.


Nested Loops
------------

Due to name-checking, gtimer does not support inner loops which are anonymous--all inner timed loops must be named (plain inner loops using non-unique stamps are OK).  Inner loop objects must be (re-)instantiated within the outer loop.


Registered Stamps
-----------------

Referring back to Loop Example 2, if it is prefered for 0's to appear under the iteration record for stamps which were not encountered in a given iteration, this can be done by registering them ahead of time.  This is done by passing a list or tuple of the names to the loop constructor with the ``rgstr_stamps`` keyword arg.  The option to register stamps is also available for subdivisions (in case of conditional stamps in subfunctions called repeatedly).


By now, we've covered most of the core functionality of gtimer, but knowing a few more things might still speed up deployment.  Next is advanced stamp options.
