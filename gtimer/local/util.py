
"""
Miscellaneous internal tools used across the package, not acting on global data.
"""


def sanitize_rgstr_stamps(rgstr_stamps=None):
    if rgstr_stamps is not None:
        if not isinstance(rgstr_stamps, (list, tuple)):
            raise TypeError("Expected list or tuple for param 'rgstr_stamps' (elements passed through str()).")
        rgstr_stamps = list(set(rgstr_stamps))
        for s in rgstr_stamps:
            s = str(s)
    else:
        rgstr_stamps = list()
    return rgstr_stamps
