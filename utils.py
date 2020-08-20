def traverse_dict(dict, path):
    """gets a value in nested dictionaries across path"""
    if len(path) == 0:
        return dict
    else:
        return traverse_dict(dict, path[1:])


def find_key(d, value):
    for k, v in d.items():
        if isinstance(v, dict):
            p = find_key(v, value)
            if p:
                return [k] + p
        elif v == value:
            return [k]
