
gtimer: A global Python timer
=============================

The purpose of the gtimer package is to record timing information during Python program execution in the following manner:

- Flexible level of detail (e.g. ranging from line-by-line to function-wide)
- Flexible scope--focus on points of interest without generating extraneous data
- Automated organization of timing data (with explicit loop data)
- Span multiple functions, files, and processes
- Simple user interface for rapid deployment and adjustment
- Low performance overhead (run with it on regularly)
- Convenient output to human-readable format or spreadsheet


Why gtimer?
-----------

Have you ever written code like the following?

.. code-block:: python

    t0 = timer()
    some_statement
    some_function()
    t1 = timer()
    t_elapsed = t1 - t0
    print "Elapsed time: ", t_elapsed

That was easy, and the timing information was useful, so the program grows and so does the interest in timing detail:

.. code-block:: python

    def some_function():
        t0 = timer()
        some_statement
        some_method()
        t1 = timer()
        another_function()
        t2 = timer()
        return t2 - t1, t1 - t0

    t0 = timer()
    another_statement
    t_some_1, t_some_2 = some_function()
    t1 = timer()
    another_method()
    t2 = timer()
    print "Total time: ", t2 - t0
    print "some_method time: ", t_some_1"
    print "another_function time: ", t_some_2
    print "some_function time: ", t1 - t0
    print "another_method time: ", t2 - t1

Suddenly, the count is 11 lines of timing code permeating only 7 lines of interest.  What's worse, the signature of ``some_function`` is polluted.  That escalated quickly!  And any insertions of new timer calls into further modified code requires manual upkeep of subtractions, printing labels, not to mention your mental model of how the times relate to each other, e.g. is ``another_function`` subsequent to or a subdivision of ``some_function``?  Still, it might be so helpful to measure specific pieces that you put up with this and just try not to touch it once it is in place, despite changing interests in certain lines or subfunctions.  With gtimer, you can quickly adjust your focus, and you will never write ``t2 - t1`` again, and *especially* not ``return t2 - t1``.  The same data may be gathered as in the previous example like so:

.. code-block:: python

    import gtimer as gt

    @gt.wrap
    def some_function():
        some_statement
        some_method()
        gt.stamp('some_method')
        another_function()
        gt.stamp('another_function')

    another_statement
    some_function()
    gt.stamp('some_function')
    another_method()
    gt.stamp('another_method')
    print gt.report()

That's down to 7 lines for timing, including both the import and the decorator.  More importantly, the printed report (shown later in the examples) will clearly distinguish that ``some_method`` and ``another_function`` are subdivisions of ``some_function``, and the addition or deletion of detail as the program evolves is as simple as adding or removing a single command to mark the time.  Several timer packages are of course already available, but none has yet provided the organizational power and comprehensiveness of gtimer.  It works for you with ease across files and even processes.

Alternatives
------------

Maybe the example above is still more work to set up than running cProfile (link) or line_profiler (link), but end-to-end, from setup to investigating and presenting the data points you really want, gtimer can be the most effective solution.  cProfile is a powerful way to start analyzing a deep code base, and handsome visualization tools exist.  Yet cProfile can give too much data, from looking at *every* subfunction in the whole call stack, or not enough data, without insight into functions or subprocesses.  And it can be hard to compare one run from the next.  With line_profiler, you can easily peer inside any particular function and immediately see hotspots, but again it may provide excessive data from lines with simple statements, and it requires a change in how the Python script is called.  Alternatively, gtimer can focus on the interesting portions of code, streamlining the collection and interpretation of results while allowing Python scripts to run with no change in call signature.  The obvious drawback is the need to fill in timing calls inside the codebase--it is intended to make this process require as little forethought as possible.  And the low overhead should make it acceptable to always run with the timing code in place.  All of the above profiling approaches are worth considering and using for different purposes (gtimer can be used concurrently with the others!).  The following pages will demonstrate distinctive features of gtimer which make it a good short-term and long-term solution for performance monitoring.


Contents:
=========

.. toctree::
   :maxdepth: 1

   pages/basic_examples.rst
   pages/loops.rst
   pages/stamp_settings.rst
   pages/parallel.rst
   pages/reporting.rst
   pages/data_structure.rst
   pages/conclusion.rst



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

