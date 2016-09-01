

def sanitize_rgstr_stamps(rgstr_stamps):
    if not isinstance(rgstr_stamps, (list, tuple)):
        raise TypeError("Expected list or tuple for rgstr_stamps (elements passed through str()).")
    rgstr_stamps = list(set(rgstr_stamps))
    for s in rgstr_stamps:
        s = str(s)
    return rgstr_stamps