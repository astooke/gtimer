
"""
Blank functions accepting the same signature as the active ones.
"""


class TimedLoopBase(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exit(self):
        self.__exit__()


class timed_loop(TimedLoopBase):

    def __init__(self, *args, **kwags):
        pass

    def next(self):
        pass


class timed_for(TimedLoopBase):

    def __init__(self, iterable, *args, **kwargs):
        self._iterable = iterable

    def __iter__(self):
        for i in self._iterable:
            yield i
