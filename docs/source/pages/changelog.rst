
Change Log
==========

v1.0.0.b.5
---------
Bug fixes:

- ``load_pkl`` no longer broken (used to attemp to load each file twice)

v1.0.0.b.4
----------
Changes:

- Python3 compatibility.
- Commented out all mmap functions (likely weren't functional yet anyway.)


v1.0.0.b.3
----------
Changes:

- Added ``current_time`` function.
- Removed ``backdate_stamp`` function, and built backdating into ``start``, ``stamp``, and ``stop``.


v1.0.0.b.2
----------
Changes:

- Added ``backdate_stamp`` function.
- Previously named ``b_stamp`` function is now called ``blank_stamp``.


v1.0.0.b.1
----------
Changes:

- Append "(running)"  to timer name when reporting on root timer that is not stopped.

Bug fixes:

- Incomplete internal reporting call structure when providing times object.


v1.0.0.b.0
----------
Initial release.
