
"""
Hide disabled classes.
"""


class UntimedLoop(object):

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exit(self):
        pass

    def next(self):
        pass


class UntimedFor(object):

    def __init__(self, iterable):
        self.iterable = iterable

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def exit(self):
        pass

    def __iter__(self):
        for i in self.iterable:
            yield i
