
G-Timer :   A Global Python Timer
=================================

G-Timer is a Python timing tool intended for use cases ranging from quick, one-time measurements to permanent integration for recording project performance.  The main features include:

- Flexible levels of detail: lines, functions, programs, or any combination
- Automatic organization of timing data
- Easy deployment and adjustment of measurements
- Convenient output to human-readable format or spreadsheet


Why G-Timer?
------------

Consider a simple in-place timing measurement:

.. code-block:: python

    t0 = timer()
    some_statement
    some_function()
    t1 = timer()
    t_elapsed = t1 - t0
    print "Elapsed time: ", t_elapsed

It was easy, and the timing information was useful, so the program grows and so does the interest in timing detail:

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

That grew cumbersome quickly!  Function signatures are polluted, a mental model of timing relationships is now necessary, and adaptation to future code development will require time-consuming effort.  All of these side-effects are eliminated with G-Timer:

.. literalinclude:: examples/index.py

.. literalinclude:: examples/index.txt

Code clutter is dramatically reduced, timing relationships are portrayed naturally, and adaptation is made easy.  The timing data structure is built dynamically as the code executes, so the user can program G-Timer linearly and with minimal forethought.  And G-Timer spans files--simply import it to act with the same timer anywhere in a program.  Standard profiling is a powerful measurement alternative, but in comparison, G-Timer can streamline the interpretation of results, does not require a change in script call signature, and makes it easier to compare separate runs.  Beyond this first example, more advanced capabilities are demonstrated in this documentation.


Contents:
=========

Sections 1-3 are for getting started.  The remainder cover advanced topics.

.. toctree::
   :maxdepth: 1
   :numbered:

   pages/installation.rst
   pages/intro_examples.rst
   pages/loops.rst
   pages/stamp_settings.rst
   pages/parallel.rst
   pages/data_structure.rst
   pages/disabled.rst
   pages/functions.rst
   pages/changelog.rst



Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

