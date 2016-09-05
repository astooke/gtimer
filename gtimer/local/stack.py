
"""
Data structure for the timer and loop hierarchies (elements held within an
instantiated structure will be individual timers or loops, see .private.focus).
"""


class Stack(object):

    def __init__(self, obj_class):
        self.stack = []
        self.obj_class = obj_class

    def create_next(self, *args, **kwargs):
        self.stack.append(self.obj_class(*args, **kwargs))
        return self.stack_return()

    def remove_last(self):
        try:
            self.stack.pop()
        except IndexError:
            pass
        finally:
            return self.stack_return()

    def stack_return(self):
        current = None if len(self) < 1 else self[-1]
        previous = None if len(self) < 2 else self[-2]
        return current, previous

    def __len__(self):
        return len(self.stack)

    def __getitem__(self, key):
        return self.stack[key]
