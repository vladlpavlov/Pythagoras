from persidict import PersiDict

def build_timeline_from_persidict(a_dict: PersiDict)->list:
    """Build a timeline from a PersiDict.

    The function returns a list of values from the dictionary,
    sorted by their modification timestamps.
    More old values come first. More recent values come last.
    """

    all_values  = []
    for key, value in a_dict.items():
        timestamp = a_dict.mtimestamp(key)
        all_values.append((timestamp, key, value))
    all_values.sort(key=lambda x: x[0])
    result = [x[2] for x in all_values]
    return result



