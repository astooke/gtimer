"""
LIFO list.
Can move the focus (current item of interest) along the list.
Always returns the current (new) focus after action.
(Hidden from user.)
"""


class FocusedStack(object):

    def __init__(self, obj_class):
        self.stack = []
        self.focus = None
        self.focus_index = None
        self.fell_off_root = False
        self.fell_off_last = False
        self.obj_class = obj_class

    def create_next(self, *args, **kwargs):
        self.stack.append(self.obj_class(*args, **kwargs))
        self.fell_off_root = False
        self.fell_off_last = False
        return self.focus_last()

    def remove_last(self):
        try:
            self.stack.pop()
        except IndexError:
            pass
        finally:
            return self.focus_last()

    def pop_last(self):
        try:
            last = self.stack.pop()
            self.focus_last()
            return last
        except IndexError:
            pass

    def focus_backward(self):
        if self.focus is not None:
            if self.focus_index > 0:
                self.focus_index -= 1
                self.focus = self.stack[self.focus_index]
            else:
                self.focus = None
                self.focus_index = None
                self.fell_off_root = True
        elif self.fell_off_last:
            self.focus_last()
        return self.focus

    def focus_forward(self):
        if self.focus is not None:
            try:
                self.focus = self.stack[self.focus_index + 1]
                self.focus_index += 1
            except IndexError:
                self.focus = None
                self.focus_index = None
                self.fell_off_last = True
        elif self.fell_off_root:
            self.focus_root()
        return self.focus

    def focus_last(self):
        try:
            self.focus = self.stack[-1]
            self.focus_index = len(self.stack) - 1
        except IndexError:
            self.focus = None
            self.focus_index = None
        finally:
            self.fell_off_root = False
            self.fell_off_last = False
            return self.focus

    def focus_root(self):
        try:
            self.focus = self.stack[0]
            self.focus_index = 0
        except IndexError:
            self.focus = None
            self.focus_index = None
        finally:
            self.fell_off_root = False
            self.fell_off_last = False
            return self.focus
