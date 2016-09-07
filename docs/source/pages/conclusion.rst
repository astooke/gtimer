
Conclusion
==========

Alternatives to Timing
----------------------

Maybe the example above is still more work to set up than running cProfile (link) or line_profiler (link), but end-to-end, from setup to investigating and presenting the data points you really want, gtimer can be the most effective solution.  cProfile is a powerful way to start analyzing a deep code base, and handsome visualization tools exist.  Yet cProfile can give too much data, from looking at *every* subfunction in the whole call stack, or not enough data, without insight into functions or subprocesses.  And it can be hard to compare one run from the next.  With line_profiler, you can easily peer inside any particular function and immediately see hotspots, but again it may provide excessive data from lines with simple statements, and as with cProfile it requires a change in how the Python script is called.  Alternatively, gtimer can focus on the interesting portions of code, streamlining the collection and interpretation of results while allowing Python scripts to run with no change in call signature.  The obvious drawback is the need to fill in timing calls inside the codebase--it is intended to make this process require as little forethought as possible.  And the low overhead should make it acceptable to always run with the timing code in place.  All of the above profiling approaches are worth considering and using for different purposes, and they can be used concurrently with gtimer.  The following pages will demonstrate distinctive features of gtimer which make it a good short-term and long-term solution for performance monitoring.


Should describe disabled mode.

Should refer to the list of method documentation.

Should build the method documentation.