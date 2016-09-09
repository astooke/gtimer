
"""
All gtimer-specific exception classes.
"""


class GTimerError(Exception):
    pass


class StoppedError(GTimerError):
    pass


class PausedError(GTimerError):
    pass


class UniqueNameError(GTimerError):
    pass


class LoopError(GTimerError):
    pass


class StartError(GTimerError):
    pass


class BackdateError(GTimerError):
    pass
