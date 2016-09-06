
Reporting
=========

Two methods exist for reporting timing data, either formatted for human-readable display or delimited for importing into a spreadsheet.  A third command, ``write_structure()`` returns a formatted string showing the heirarchical tree structure of the timer and its subdivisions.  


1. All-Purpose Reporting: ``report()``
--------------------------------------

This function returns a string as printed in the previous examples.  The first argument is optional as a ``times`` instance, or else the current root timer is reported on.  In cases where a timer has parallel subdivisions, the subdivision with the longest total time is used for display and these entries are marked (contents of others are ignored).  A dictionary of formatting options may be input to this command, see the docstring for details.


2. Parallel or Multi-Timer Comparisons: ``compare()``
-----------------------------------------------------

This function was not demonstrated in the examples.  It is intended to make it easy to compare different runs of similar code or to compare timing data from parallel workers under a master timer.  It accepts an optional first argument that is a list of ``times`` instances.  If provided, the comparison populates a full hierarchy of stamps present in any member of the list and prints total and stamp values for all members side-by-side, leaving blanks where members did not report on a stamp.  Again, where parallel subdvisions of these instances are encountered, only the maximum total time subdivision is used (``compare()`` does not branch).  If the first argument is not provided, this function defaults to examining all parallel subdivisions of the current timer at the root level.  Parallel comparisons further down the hierarchy require the lists to be retrieved and fed to ``compare()`` (see next section). Similar reporting and formatting options are available as for ``report()``, see the docstring for details.